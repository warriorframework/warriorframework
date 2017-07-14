<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes"/>

<xsl:template match="/testsuites">
	<xsl:element name="testsuites">
		<xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
		<xsl:attribute name="time"><xsl:value-of select="@time"/></xsl:attribute>  
		<xsl:attribute name="tests"><xsl:value-of select="@tests"/></xsl:attribute>
		<xsl:attribute name="failures"><xsl:value-of select="@failures"/></xsl:attribute>
		<xsl:attribute name="errors"><xsl:value-of select="@errors"/></xsl:attribute>
		<xsl:for-each select="./testsuite">
			<xsl:element name="testsuite">
				<xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
				<xsl:attribute name="time"><xsl:value-of select="@time"/></xsl:attribute>
				<xsl:attribute name="timestamp"><xsl:value-of select="@timestamp"/></xsl:attribute>
				<xsl:attribute name="tests"><xsl:value-of select="@tests"/></xsl:attribute>
				<xsl:attribute name="failures"><xsl:value-of select="@failures"/></xsl:attribute>
				<xsl:attribute name="errors"><xsl:value-of select="@errors"/></xsl:attribute>
				<xsl:attribute name="skipped"><xsl:value-of select="@skipped"/></xsl:attribute>
				<xsl:for-each select="./testcase">
				<xsl:element name="testcase">
					<xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
					<xsl:attribute name="classname"><xsl:value-of select="@classname"/></xsl:attribute>
					<xsl:attribute name="time"><xsl:value-of select="@time"/></xsl:attribute>
					<xsl:attribute name="timestamp"><xsl:value-of select="@timestamp"/></xsl:attribute>
					<xsl:if test="failure">
						<xsl:element name="failure">
							<xsl:attribute name="message"><xsl:value-of select="@message"/></xsl:attribute>
						</xsl:element>						
					</xsl:if>
					<xsl:if test="error">
						<xsl:element name="error">
							<xsl:attribute name="message"><xsl:value-of select="@message"/></xsl:attribute>
						</xsl:element>						
					</xsl:if>
					<xsl:if test="skipped">
						<xsl:element name="skipped">
							<xsl:attribute name="message"><xsl:value-of select="@message"/></xsl:attribute>
						</xsl:element>						
					</xsl:if>
				</xsl:element>
				</xsl:for-each>
			</xsl:element>
		</xsl:for-each>
	</xsl:element>	
 </xsl:template>
</xsl:stylesheet>
