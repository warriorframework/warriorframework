var projectSpec = {
		onchange: function(){
		//console.log("I been changed now!")
		},
		validate: function(obj){
		//console.log("I be validatin' now!")
		},
		elements: {
		"Project": {
				menu: [{
					caption: "Append a <Details>",
					action: Xonomy.newElementChild,
					actionParameter: "<Details><Name>Name</Name><Title>Title</Title><Engineer>\
					</Engineer><Date></Date><Time></Time><default_onError action=\"next\"/></Details>",
					hideIf: function(jsElement) {
						return jsElement.hasChildElement("Details");
					}
				}]
			},
		"Details": {
			mustBeBefore: ["Testsuites",]
			},
		"Testsuites": {
				menu: [{
					caption: "Append a <Testsuite>",
					action: Xonomy.newElementChild,
					actionParameter: "<Testsuite>" + 
				            "<path>../suites/framework_tests/MUST_SET_FILE_NAME_HERE.xml</path>" + 
            				'<Execute ExecType="Yes"/><onError action="next" value=""/><runmode type="rmt" value="2"/><impact>impact</impact></Testsuite>',

				}]
			},
		"Execute": {
			menu: [{
					caption: "Append a <Rule>",
					action: Xonomy.newElementChild,
					actionParameter: "<Rule Condition=\"\" Condvalue=\"\" Else=\"\" Elsevalue=\"\"></Rule>"
					}],
			attributes:{
				"ExecType": {
						asker: Xonomy.askPicklist,
						askerParameter: [ "Yes","No" ]
					}
				}
			},
		"Rule": {
				menu: [{
					caption: "Add a <Rule>",
					action: Xonomy.newElementAfter,
					actionParameter: "<Rule Condition=\"\" Condvalue=\"\" Else=\"\" Elsevalue=\"\"></Rule>"
					},
					{
					caption: "Delete this <Rule>",
					action: Xonomy.deleteElement
				}],attributes: {
				"Condition": {
						asker: Xonomy.askString
					},
				"Condvalue": {
						asker: Xonomy.askString
					},
				"Else": {
						asker: Xonomy.askPicklist,
						askerParameter: [ "Yes","No" ]
					},
				"Elsevalue": {
						asker: Xonomy.askString
					}
			}
		},
		"onError": {
			menu: [{
				caption: "Add @label=\"something\"",
				action: Xonomy.newAttribute,
				actionParameter: {name: "label", value: "something"},
				hideIf: function(jsElement){
					return jsElement.hasAttribute("label");
					}
				}],
			attributes: {
					"action": {
						asker: Xonomy.askPicklist,
						askerParameter: [ "next","stop" ]
					}, 
					"value": {
						asker: Xonomy.askOpenPicklist,
						askerParameter: [ {value: "n", caption: "next"}, {value: "s", caption: "stop"} ]
					}, 
					"label": {
						asker: Xonomy.askOpenPicklist,
						askerParameter: [ {value: "n", caption: "next"}, {value: "s", caption: "stop"} ]
					}
				}
			},

		"Testsuite": {
			menu: [{
				caption: "Add @label=\"something\"",
				action: Xonomy.newAttribute,
				actionParameter: {name: "label", value: "something"},
				hideIf: function(jsElement){
					return jsElement.hasAttribute("TestSuite");
					}
				}, {
				caption: "Delete this <item>",
				action: Xonomy.deleteElement
				}, {
				caption: "New <Testsuite> before this",
				action: Xonomy.newElementBefore,
				actionParameter: "<Testsuite>" + 
				            "<path>../suites/framework_tests/ts_runmode_rmt_at_suite_level.xml</path>" + 
            				'<Execute ExecType="Yes"/><onError action="next" value=""/><runmode type="rmt" value="2"/><impact>impact</impact></Testsuite>',
				}, {
				caption: "New <Testsuite> after this",
				action: Xonomy.newElementAfter,
				actionParameter: "<Testsuite>" + 
				            "<path>../suites/an.xml</path>" + 
            				'<Execute ExecType="Yes"/><onError action="next" value=""/><runmode type="rmt" value="2"/><impact>impact</impact></Testsuite>',
				}],
			canDropTo: ["TestSuite", "Testsuites"],
			attributes: {
			"label": {
				asker: Xonomy.askString,
				menu: [{
					caption: "Delete this @label",
					action: Xonomy.deleteAttribute
					}]
				}
			
			}
		}
	}
};