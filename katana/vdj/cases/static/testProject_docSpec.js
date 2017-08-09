var projectSpec = {
		onchange: function(){
		console.log("I been changed now!")
		},
		validate: function(obj){
		console.log("I be validatin' now!")
		},
		elements: {
		"Testsuites": {
				menu: [{
					caption: "Append an <item>",
					action: Xonomy.newElementChild,
					actionParameter: "<TestSuites/>"
				}]
			},
		"onError": {
			menu: [{
				caption: "Add @label=\"something\"",
				action: Xonomy.newAttribute,
				actionParameter: {name: "label", value: "something"},
				hideIf: function(jsElement){
					return jsElement.hasAttribute("TestSuite");
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
				}, {
			}],
			canDropTo: ["TestSuite"],
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