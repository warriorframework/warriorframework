var caseSpec = {
		onchange: function(){
		console.log("I been changed now!")
		},
		validate: function(obj){
		console.log("I be validatin' now!")
		},
		elements: {
		"steps": {
				menu: [{
					caption: "Append an <item>",
					action: Xonomy.newElementChild,
					actionParameter: "<steps/>"
				}]
				},
		"Requirements": {
			menu: [ {
				caption: "Delete this <item>",
				action: Xonomy.deleteElement
				}, {
				caption: "New <Requirement> before this",
				action: Xonomy.newElementBefore,
				actionParameter: "<Requirement>" ,
				}, {
				caption: "New <Requirement> after this",
				action: Xonomy.newElementAfter,
				actionParameter: "<Requirement>",
				}, {
			}],
		},
		"step": {
			menu: [{
				caption: "Add @label=\"something\"",
				action: Xonomy.newAttribute,
				actionParameter: {name: "label", value: "something"},
				hideIf: function(jsElement){
					return jsElement.hasAttribute("step");
					}
				}, {
				caption: "Delete this <item>",
				action: Xonomy.deleteElement
				}, {
				caption: "New <step> before this",
				action: Xonomy.newElementBefore,
				actionParameter: "<step>" + 
				            "<path>../suites/framework_tests/ts_runmode_rmt_at_suite_level.xml</path>" +
            				'<Execute ExecType="Yes"/><onError action="next" value=""/><runmode type="rmt" value="2"/><impact>impact</impact></step>',
				}, {
				caption: "New <step> after this",
				action: Xonomy.newElementAfter,
				actionParameter: "<step>" + 
				            "<path>../suites/an.xml</path>" + 
				            '<Descripton>Description..</Description><iteration_type type="" />' +
            				'<Execute ExecType="Yes"/><onError action="next" value=""/><runmode type="rmt" value="2"/><impact>impact</impact></step>',
				}, {
			}],
			canDropTo: ["step"],
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