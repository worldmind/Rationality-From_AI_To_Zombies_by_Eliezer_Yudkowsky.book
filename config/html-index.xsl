<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xi="http://www.w3.org/2001/XInclude"
    version="1.0">

<xsl:output method="html" indent="yes" encoding="UTF-8"/>

<!--Input file is *.html with description of the collection-->

<!--Paths from run directory-->
<xsl:param name="html_files"/>

<xsl:variable name="delimiter" select="' '"/>
<xsl:variable name="db_ext" select="'.db'"/>
<xsl:variable name="book_file" select="'index.html'"/>

<xsl:template match="/">

<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Rationality: A-Z</title>
    <link rel="stylesheet" href="css/style.css"/>
</head>
<body>
    <h3>Rationality: A-Z</h3>
    <xsl:copy-of select="node()/body/*"/>
    <hr/>
    <p>The collection is also available here:</p>
    <div class="book_set">
        <ol>
        <xsl:call-template name="get_file">
            <xsl:with-param name="files" select="$html_files"/>
        </xsl:call-template>
        </ol>
    </div>
    <hr/>
</body>
</html>

</xsl:template>

<xsl:template name="get_file">
    <xsl:param name="files"/>
    <xsl:if test="string-length($files)">
        <xsl:variable name="file" select="substring-before(concat($files, $delimiter), $delimiter)"/>
        <xsl:call-template name="format">
            <xsl:with-param name="file" select="$file"/>
        </xsl:call-template>
        <xsl:call-template name="get_file">
            <xsl:with-param name="files" select="substring-after($files,$delimiter)"/>
        </xsl:call-template>
    </xsl:if>
</xsl:template>

<xsl:template name="format">
    <xsl:param name="file"/>

    <!--path from index.html to */index.html -->
    <xsl:variable name="rel_path" select="substring-after($file, '/')"/>

        <li><a href="{$rel_path}">
        <xsl:call-template name="get_title">
            <xsl:with-param name="file" select="$file"/>
        </xsl:call-template>
        </a></li>

</xsl:template>

<xsl:template name="get_title">
    <xsl:param name="file"/>

    <!--get "title" from *.db file with correct xml-structure -->
    <xsl:variable name="db_path" select="concat(substring-before($file, concat('/', $book_file)), $db_ext)"/>
    <xsl:variable name="title" select="document($db_path, /)/div/ttl"/>
    <xsl:value-of select="normalize-space($title)"/>
</xsl:template>

</xsl:stylesheet>

