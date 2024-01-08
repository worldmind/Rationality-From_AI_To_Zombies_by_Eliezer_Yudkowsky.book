<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xi="http://www.w3.org/2001/XInclude"
    version="1.0">

<xsl:output method="xml" indent="yes"/>

<xsl:param name="dbk_files"/>
<xsl:param name="dbk_dir"/>
<xsl:param name="target_ext"/>
<xsl:variable name="db_ext" select="'.db'"/>
<xsl:variable name="root_dir" select="'../'"/>
<xsl:variable name="delimiter" select="' '"/>

<xsl:template match="/">
<targetset>
    <sitemap>
        <dir name=".">
    <xsl:call-template name="item">
        <xsl:with-param name="files" select="$dbk_files"/>
    </xsl:call-template>
        </dir>
    </sitemap>
</targetset>
</xsl:template>

<xsl:template name="item">
    <xsl:param name="files"/>
    <xsl:if test="string-length($files)">
        <xsl:variable name="file" select="substring-before(concat($files, $delimiter), $delimiter)"/>
        <xsl:call-template name="format">
            <xsl:with-param name="file" select="$file"/>
        </xsl:call-template>
        <xsl:call-template name="item">
            <xsl:with-param name="files" select="substring-after($files,$delimiter)"/>
        </xsl:call-template>
    </xsl:if>
</xsl:template>

<xsl:template name="format">
    <xsl:param name="file"/>

    <xsl:variable name="item_id" select="document(concat($root_dir, $file))/*/@xml:id"/>

    <xsl:variable name="fname" select="substring-before(substring-after($file, '/'), '.')"/>
    <xsl:variable name="file_target" select="concat($fname, $target_ext)"/>
    <xsl:variable name="file_db" select="concat($fname, $db_ext)"/>


        <document targetdoc="{$item_id}" baseuri="{$file_target}">
            <xi:include href="{$file_db}"/>
        </document>

</xsl:template>

</xsl:stylesheet>
