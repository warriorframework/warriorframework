 var projects = {

	closeCase: function(){
		katana.closeSubApp();
	},

	emailCases: {
		generalBody: '',

		init: function () {
			console.log('test auto init of app');
			Cases.emailCases.generalBody = $(this);
		},
	},


	save: function(){
		katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, katana.toJSON(), function( data ) {
			console.log('saved', data);
		});
	},
};
