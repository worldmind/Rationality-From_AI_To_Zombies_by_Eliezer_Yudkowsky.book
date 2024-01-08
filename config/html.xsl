<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:import href="/usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl"/>

<xsl:param name="section.autolabel">1</xsl:param>
<xsl:param name="section.label.includes.component.label">1</xsl:param>
<xsl:param name="keep.relative.image.uris">1</xsl:param>
<xsl:param name="disable-output-escaping">no</xsl:param>
<xsl:param name="ulink.show">0</xsl:param>
<xsl:param name="bibliography.numbered">1</xsl:param>
<xsl:param name="current.docid" select="/*/@xml:id"/>

</xsl:stylesheet>
