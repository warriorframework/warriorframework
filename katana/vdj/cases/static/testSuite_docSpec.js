var suiteSpec = {
		onchange: function(){
		console.log("I been changed now!")
		},
		validate: function(obj){
		console.log("I be validatin' now!")
		},
		elements: {
		"Testcases": {
				menu: [{
					caption: "Append <Testcases>",
					action: Xonomy.newElementChild,
					actionParameter: "<Testcases/>"
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
				}],
		},

		"Testcase": {
			menu: [{
				caption: "Add @label=\"something\"",
				action: Xonomy.newAttribute,
				actionParameter: {name: "label", value: "something"},
				hideIf: function(jsElement){
					return jsElement.hasAttribute("Testcase");
					}
				}, {
				caption: "Delete this <item>",
				action: Xonomy.deleteElement
				}, {
				caption: "New <Testcase> before this",
				action: Xonomy.newElementBefore,
				actionParameter: "<Testcase>" + 
				            "<path>../testcased/framework_tests/</path>" + 
            				'<ontext>positive</context><onError actesttion="next" value=""/><runtype>sequential_keywords</runtype><impact>impact</impact></Testcase>',
				}, {
				caption: "New <Testcase> after this",
				action: Xonomy.newElementAfter,
				actionParameter: "<Testcase>" + 
				            "<path>../testcased/framework_tests/</path>" + 
            				'<ontext>positive</context><onError actesttion="next" value=""/><runtype>sequential_keywords</runtype><impact>impact</impact></Testcase>',
				}],
			canDropTo: ["Testcase"],
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