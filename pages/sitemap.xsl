<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
                xmlns:html="http://www.w3.org/TR/REC-html40"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN">
      <head>
        <title>XML Sitemap | 拉玛那马哈希知识库</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style type="text/css">
          body {
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Serif SC", sans-serif;
            color: #1A2332;
            background-color: #FAF7F2;
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
          }
          .container {
            max-width: 1060px;
            margin: 0 auto;
            background: #FFFFFF;
            padding: 36px 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px -10px rgba(26, 35, 50, 0.08);
            border: 1px solid #E0D6C8;
          }
          .header-box {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #F3EDE4;
            padding-bottom: 20px;
            margin-bottom: 24px;
          }
          .logo-title {
            font-size: 24px;
            font-weight: 800;
            color: #1A2332;
            margin: 0;
            letter-spacing: -0.01em;
          }
          .logo-title span {
            color: #B8860B;
          }
          .subtitle {
            font-size: 14px;
            color: #6B6560;
            margin-bottom: 24px;
            line-height: 1.6;
          }
          .subtitle a {
            color: #8B5E0B;
            text-decoration: none;
            font-weight: 600;
          }
          .subtitle a:hover {
            text-decoration: underline;
          }
          .badge-count {
            display: inline-block;
            background: #FFF8EE;
            color: #B8860B;
            border: 1px solid #E0D6C8;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            margin-top: 10px;
          }
          th {
            background-color: #1A2332;
            color: #D4A843;
            padding: 12px 16px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          th:first-child {
            border-top-left-radius: 8px;
          }
          th:last-child {
            border-top-right-radius: 8px;
          }
          tr:hover td {
            background-color: #FFF8EE;
          }
          td {
            padding: 12px 16px;
            border-bottom: 1px solid #F3EDE4;
            font-size: 14px;
            word-break: break-all;
          }
          td a {
            color: #1A2332;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
          }
          td a:hover {
            color: #B8860B;
            text-decoration: underline;
          }
          .priority-badge {
            display: inline-block;
            padding: 2px 8px;
            background-color: rgba(184, 134, 11, 0.12);
            color: #8B5E0B;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
          }
          .lang-link {
            font-size: 11px;
            background: #F3EDE4;
            color: #6B6560;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 6px;
            text-decoration: none;
          }
          .lang-link:hover {
            background: #E0D6C8;
          }
          .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #F3EDE4;
            font-size: 12px;
            color: #6B6560;
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header-box">
            <h1 class="logo-title">拉玛那马哈希 <span>XML Sitemap</span></h1>
            <a href="https://ramanamaharshi.space" style="color: #8B5E0B; font-weight: 600; text-decoration: none; font-size: 14px;">返回首页 →</a>
          </div>

          <p class="subtitle">
            本 XML 站点地图供 Google、Bing 等搜索引擎检索。格式标准参考自 <a href="https://sitemaps.org" target="_blank">sitemaps.org</a>。
          </p>

          <!-- 如果是 Sitemap Index 索引模式 -->
          <xsl:if test="sitemap:sitemapindex">
            <div style="margin-bottom: 16px;">
              <span class="badge-count">
                Sitemap Index 包含了 <xsl:value-of select="count(sitemap:sitemapindex/sitemap:sitemap)"/> 个分类地图文件
              </span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Sitemap 分类地图 URL</th>
                  <th style="width: 180px;">最后修改日期</th>
                </tr>
              </thead>
              <tbody>
                <xsl:for-each select="sitemap:sitemapindex/sitemap:sitemap">
                  <tr>
                    <td>
                      <a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a>
                    </td>
                    <td>
                      <xsl:value-of select="sitemap:lastmod"/>
                    </td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </xsl:if>

          <!-- 如果是具体 URL 列表模式 -->
          <xsl:if test="sitemap:urlset">
            <div style="margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
              <span class="badge-count">
                当前地图共计包含 <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> 个页面
              </span>
              <a href="/sitemap.xml" style="font-size: 13px; color: #8B5E0B; text-decoration: none;">← 返回 Sitemap 总索引</a>
            </div>
            <table>
              <thead>
                <tr>
                  <th>页面 URL</th>
                  <th style="width: 130px;">更新频率</th>
                  <th style="width: 120px;">最后修改</th>
                  <th style="width: 80px; text-align: center;">优先级</th>
                </tr>
              </thead>
              <tbody>
                <xsl:for-each select="sitemap:urlset/sitemap:url">
                  <tr>
                    <td>
                      <a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a>
                      <xsl:for-each select="xhtml:link">
                        <a class="lang-link" href="{@href}"><xsl:value-of select="@hreflang"/></a>
                      </xsl:for-each>
                    </td>
                    <td>
                      <xsl:value-of select="sitemap:changefreq"/>
                    </td>
                    <td>
                      <xsl:value-of select="sitemap:lastmod"/>
                    </td>
                    <td style="text-align: center;">
                      <span class="priority-badge">
                        <xsl:value-of select="sitemap:priority"/>
                      </span>
                    </td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </xsl:if>

          <div class="footer">
            拉玛那马哈希知识库 · 网页版 XML Sitemap
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
