/**
 * 拉玛那马哈希知识库 - 音频朗读引擎 (Audio Reader / Text-To-Speech)
 * 支持正文自动识别、分句朗读、实时文本高亮与平滑滚动、语速与发音人控制。
 */
(function () {
    'use strict';

    class AudioReader {
        constructor() {
            this.supported = typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
            this.synth = this.supported ? window.speechSynthesis : null;
            this.utterance = null;
            this.voices = [];
            this.selectedVoice = null;
            this.rate = 1.0;
            this.isPlaying = false;
            this.isPaused = false;
            this.chunks = []; // { text: string, element: HTMLElement }
            this.currentIndex = 0;
            this.totalWords = 0;
            this.estimatedMinutes = 0;
            this.container = null;
            this.headerBtnEl = null;
            this.floatingPlayerEl = null;
        }

        init() {
            if (!this.supported) return;

            // 避免重复初始化
            if (document.getElementById('tts-header-bar')) return;

            // 限制只在包含正文内容的文章页面生效
            this.container = document.querySelector('.content-wrapper');
            if (!this.container) return;

            // 提取待朗读的可读节点
            this.extractChunks();
            if (this.chunks.length === 0 || this.totalWords < 60) {
                // 字数太少则不挂载
                return;
            }

            this.estimatedMinutes = Math.max(1, Math.ceil(this.totalWords / 250));

            // 初始化声线列表
            this.loadVoices();
            if (typeof speechSynthesis !== 'undefined' && speechSynthesis.onvoiceschanged !== undefined) {
                speechSynthesis.onvoiceschanged = () => this.loadVoices();
            }

            // 创建页面顶部“听这篇文章”操作条
            this.renderHeaderButton();

            // 创建底部悬浮播放器
            this.renderFloatingPlayer();

            // 绑定页面销毁/切页事件，释放语音播放
            window.addEventListener('beforeunload', () => this.stop());
        }

        loadVoices() {
            if (!this.synth) return;
            const allVoices = this.synth.getVoices() || [];
            // 过滤中文发音人 (zh-CN, zh-TW, zh-HK)
            this.voices = allVoices.filter(v => v.lang.includes('zh') || v.lang.includes('ZH') || v.lang.includes('cmn'));

            if (this.voices.length === 0) {
                // 降级：如果未明确标注 zh 语言，保留全量供选择
                this.voices = allVoices;
            }

            // 挑选推荐语音：优先自然流畅的女声/男声（如 Xiaoxiao, Yunxi, Ting-Ting 等）
            const preferred = this.voices.find(v =>
                v.name.includes('Xiaoxiao') ||
                v.name.includes('Yunxi') ||
                v.name.includes('Ting-Ting') ||
                v.name.includes('Yu-shu') ||
                v.name.includes('Natural')
            );

            this.selectedVoice = preferred || (this.voices.length > 0 ? this.voices[0] : null);

            // 更新播放器声线下拉列表
            this.updateVoiceSelectOptions();
        }

        extractChunks() {
            this.chunks = [];
            this.totalWords = 0;

            // 选取正文中有实际阅读意义的元素
            const elements = this.container.querySelectorAll('h1, h2, h3, h4, p, blockquote, li, .quote-box');

            elements.forEach(el => {
                // 排除导航、按钮、无关面板等
                if (el.closest('.page-nav') || el.closest('.breadcrumb') || el.closest('#tts-header-bar') || el.closest('.tag')) {
                    return;
                }

                // 提取干净的纯文本
                let text = el.innerText || el.textContent || '';
                text = text.trim();

                // 去除掉冗余无用的空字符串或图标
                if (text.length > 1 && !/^[\s\t\n\r]*$/.test(text)) {
                    this.chunks.push({
                        text: text,
                        element: el
                    });
                    this.totalWords += text.length;
                }
            });
        }

        renderHeaderButton() {
            const titleEl = this.container.querySelector('.chapter-title, h1') || this.container.firstElementChild;
            if (!titleEl) return;

            const headerBar = document.createElement('div');
            headerBar.id = 'tts-header-bar';
            headerBar.className = 'tts-header-bar';
            headerBar.innerHTML = `
                <button class="tts-play-btn" id="tts-start-btn">
                    <span class="tts-icon">🎧</span>
                    <span class="tts-text">听这篇文章</span>
                    <span class="tts-meta">· 约 ${this.estimatedMinutes} 分钟</span>
                </button>
            `;

            // 插入在标题下方
            if (titleEl.nextSibling) {
                titleEl.parentNode.insertBefore(headerBar, titleEl.nextSibling);
            } else {
                titleEl.parentNode.appendChild(headerBar);
            }

            const startBtn = headerBar.querySelector('#tts-start-btn');
            startBtn.addEventListener('click', () => {
                if (this.isPlaying) {
                    if (this.isPaused) {
                        this.resume();
                    } else {
                        this.pause();
                    }
                } else {
                    this.playFrom(0);
                }
            });
        }

        renderFloatingPlayer() {
            const floating = document.createElement('div');
            floating.id = 'tts-floating-player';
            floating.className = 'tts-floating-player tts-hidden';

            floating.innerHTML = `
                <div class="tts-player-inner">
                    <div class="tts-info">
                        <span class="tts-badge">🎧 音频朗读</span>
                        <span class="tts-current-text" id="tts-status-text">准备就绪</span>
                    </div>

                    <div class="tts-controls">
                        <button class="tts-ctrl-btn" id="tts-prev-btn" title="上一段">⏮</button>
                        <button class="tts-ctrl-btn tts-main-toggle" id="tts-toggle-btn" title="播放/暂停">▶</button>
                        <button class="tts-ctrl-btn" id="tts-next-btn" title="下一段">⏭</button>
                        <button class="tts-ctrl-btn" id="tts-stop-btn" title="停止">⏹</button>
                    </div>

                    <div class="tts-progress-container" id="tts-progress-bar">
                        <div class="tts-progress-fill" id="tts-progress-fill" style="width: 0%;"></div>
                    </div>

                    <div class="tts-settings">
                        <div class="tts-speed-selector">
                            <button class="tts-speed-btn" id="tts-speed-btn">1.0x</button>
                            <div class="tts-speed-dropdown tts-hidden" id="tts-speed-menu">
                                <span data-rate="0.8">0.8x</span>
                                <span data-rate="1.0" class="active">1.0x</span>
                                <span data-rate="1.25">1.25x</span>
                                <span data-rate="1.5">1.5x</span>
                                <span data-rate="2.0">2.0x</span>
                            </div>
                        </div>

                        <select class="tts-voice-select" id="tts-voice-select" title="发音人选择"></select>
                        <button class="tts-close-btn" id="tts-close-btn" title="收起播放面板">✕</button>
                    </div>
                </div>
            `;

            document.body.appendChild(floating);
            this.floatingPlayerEl = floating;

            this.bindPlayerEvents();
            this.updateVoiceSelectOptions();
        }

        updateVoiceSelectOptions() {
            if (!this.floatingPlayerEl) return;
            const select = this.floatingPlayerEl.querySelector('#tts-voice-select');
            if (!select) return;

            select.innerHTML = '';
            if (this.voices.length === 0) {
                const opt = document.createElement('option');
                opt.value = '';
                opt.textContent = '默认中文声音';
                select.appendChild(opt);
                return;
            }

            this.voices.forEach((v, idx) => {
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = `${v.name} (${v.lang})`;
                if (this.selectedVoice && v.name === this.selectedVoice.name) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });
        }

        bindPlayerEvents() {
            if (!this.floatingPlayerEl) return;

            const toggleBtn = this.floatingPlayerEl.querySelector('#tts-toggle-btn');
            const prevBtn = this.floatingPlayerEl.querySelector('#tts-prev-btn');
            const nextBtn = this.floatingPlayerEl.querySelector('#tts-next-btn');
            const stopBtn = this.floatingPlayerEl.querySelector('#tts-stop-btn');
            const closeBtn = this.floatingPlayerEl.querySelector('#tts-close-btn');
            const progressBar = this.floatingPlayerEl.querySelector('#tts-progress-bar');
            const speedBtn = this.floatingPlayerEl.querySelector('#tts-speed-btn');
            const speedMenu = this.floatingPlayerEl.querySelector('#tts-speed-menu');
            const voiceSelect = this.floatingPlayerEl.querySelector('#tts-voice-select');

            toggleBtn.addEventListener('click', () => {
                if (this.isPlaying) {
                    if (this.isPaused) this.resume();
                    else this.pause();
                } else {
                    this.playFrom(this.currentIndex);
                }
            });

            prevBtn.addEventListener('click', () => {
                if (this.currentIndex > 0) {
                    this.playFrom(this.currentIndex - 1);
                }
            });

            nextBtn.addEventListener('click', () => {
                if (this.currentIndex < this.chunks.length - 1) {
                    this.playFrom(this.currentIndex + 1);
                }
            });

            stopBtn.addEventListener('click', () => this.stop());
            closeBtn.addEventListener('click', () => this.hideFloatingPlayer());

            // 进度条点击跳转段落
            progressBar.addEventListener('click', (e) => {
                const rect = progressBar.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const ratio = Math.max(0, Math.min(1, clickX / rect.width));
                const targetIndex = Math.floor(ratio * this.chunks.length);
                this.playFrom(targetIndex);
            });

            // 语速菜单显示/隐藏
            speedBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                speedMenu.classList.toggle('tts-hidden');
            });

            document.addEventListener('click', () => {
                if (speedMenu && !speedMenu.classList.contains('tts-hidden')) {
                    speedMenu.classList.add('tts-hidden');
                }
            });

            speedMenu.querySelectorAll('span').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const rateVal = parseFloat(item.getAttribute('data-rate'));
                    this.rate = rateVal;
                    speedBtn.textContent = `${rateVal}x`;

                    speedMenu.querySelectorAll('span').forEach(s => s.classList.remove('active'));
                    item.classList.add('active');
                    speedMenu.classList.add('tts-hidden');

                    // 如果正在播放，重播当前段落生效新语速
                    if (this.isPlaying && !this.isPaused) {
                        this.playFrom(this.currentIndex);
                    }
                });
            });

            // 发音人选择
            voiceSelect.addEventListener('change', (e) => {
                const idx = parseInt(e.target.value);
                if (this.voices[idx]) {
                    this.selectedVoice = this.voices[idx];
                    if (this.isPlaying && !this.isPaused) {
                        this.playFrom(this.currentIndex);
                    }
                }
            });
        }

        playFrom(index) {
            if (!this.synth) return;

            if (index < 0) index = 0;
            if (index >= this.chunks.length) {
                this.finish();
                return;
            }

            this.synth.cancel(); // 停止先前的朗读

            this.currentIndex = index;
            this.isPlaying = true;
            this.isPaused = false;

            const chunk = this.chunks[index];

            // 构造朗读对象
            const u = new SpeechSynthesisUtterance(chunk.text);
            u.rate = this.rate;
            if (this.selectedVoice) {
                u.voice = this.selectedVoice;
            }

            u.onstart = () => {
                this.updateUI();
                this.highlightChunk(chunk);
            };

            u.onend = () => {
                this.clearHighlight();
                if (this.isPlaying && !this.isPaused) {
                    this.playFrom(this.currentIndex + 1);
                }
            };

            u.onerror = (err) => {
                console.warn('TTS朗读报错:', err);
                this.clearHighlight();
                // 尝试播放下一句
                if (this.isPlaying && this.currentIndex < this.chunks.length - 1) {
                    setTimeout(() => this.playFrom(this.currentIndex + 1), 200);
                } else {
                    this.stop();
                }
            };

            this.utterance = u;
            this.synth.speak(u);

            this.showFloatingPlayer();
            this.updateUI();
        }

        pause() {
            if (!this.synth) return;
            if (this.isPlaying && !this.isPaused) {
                this.synth.pause();
                this.isPaused = true;
                this.updateUI();
            }
        }

        resume() {
            if (!this.synth) return;
            if (this.isPlaying && this.isPaused) {
                this.synth.resume();
                this.isPaused = false;
                this.updateUI();
            } else if (!this.isPlaying) {
                this.playFrom(this.currentIndex);
            }
        }

        stop() {
            if (this.synth) {
                this.synth.cancel();
            }
            this.isPlaying = false;
            this.isPaused = false;
            this.currentIndex = 0;
            this.clearHighlight();
            this.updateUI();
            this.hideFloatingPlayer();
        }

        finish() {
            this.stop();
            const statusText = document.getElementById('tts-status-text');
            if (statusText) statusText.textContent = '朗读已完成';
        }

        highlightChunk(chunk) {
            this.clearHighlight();
            if (chunk && chunk.element) {
                chunk.element.classList.add('tts-highlighting');

                // 平滑滚动到屏幕中央区域
                chunk.element.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        }

        clearHighlight() {
            document.querySelectorAll('.tts-highlighting').forEach(el => {
                el.classList.remove('tts-highlighting');
            });
        }

        updateUI() {
            if (!this.floatingPlayerEl) return;

            const toggleBtn = this.floatingPlayerEl.querySelector('#tts-toggle-btn');
            const statusText = this.floatingPlayerEl.querySelector('#tts-status-text');
            const progressFill = this.floatingPlayerEl.querySelector('#tts-progress-fill');
            const headerBtn = document.querySelector('#tts-start-btn .tts-text');

            const pct = Math.min(100, Math.round(((this.currentIndex + 1) / this.chunks.length) * 100));
            if (progressFill) progressFill.style.width = `${pct}%`;

            if (this.isPlaying && !this.isPaused) {
                if (toggleBtn) toggleBtn.textContent = '⏸';
                if (statusText && this.chunks[this.currentIndex]) {
                    const txt = this.chunks[this.currentIndex].text;
                    statusText.textContent = `朗读中 (${pct}%): ${txt.substring(0, 18)}...`;
                }
                if (headerBtn) headerBtn.textContent = '暂停朗读';
            } else if (this.isPaused) {
                if (toggleBtn) toggleBtn.textContent = '▶';
                if (statusText) statusText.textContent = `已暂停 (${pct}%)`;
                if (headerBtn) headerBtn.textContent = '继续朗读';
            } else {
                if (toggleBtn) toggleBtn.textContent = '▶';
                if (statusText) statusText.textContent = '准备就绪';
                if (headerBtn) headerBtn.textContent = '听这篇文章';
            }
        }

        showFloatingPlayer() {
            if (this.floatingPlayerEl) {
                this.floatingPlayerEl.classList.remove('tts-hidden');
            }
        }

        hideFloatingPlayer() {
            if (this.floatingPlayerEl) {
                this.floatingPlayerEl.classList.add('tts-hidden');
            }
        }
    }

    // 暴露全局实例并自动挂载
    const reader = new AudioReader();
    window.audioReader = reader;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => reader.init());
    } else {
        reader.init();
    }
})();
