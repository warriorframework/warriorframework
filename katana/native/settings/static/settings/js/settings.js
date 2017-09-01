var settings = {

	closeSetting: function(){
		katana.closeSubApp();
	},

	emailSettings: {
		generalBody: '',

		init: function () {
			console.log('test auto init of app');
			settings.emailSettings.generalBody = $(this);
		},
	},

	encrypetion: {
		save: function(){
			katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, null, function( data ){
				console.log('saved', data);
			} );
		}
	},

	jira: {
		boolHandler: function( $elem ){
			var button = $elem.closest('.field-block').find('.relative-tool-bar [title="' + $elem.attr('key') + '"]');
			$elem.val() == 'true' && button.addClass('active');
			$elem.closest('.field').remove();
		},

		default: function(){
			settings.jira.boolHandler( $(this) );
		},

		append_log: function(){
			settings.jira.boolHandler( $(this) );
		},

		issue_type: function(){
			var $elem = this;
			var data = JSON.parse($elem.val());
			data = Array.isArray(data) ? data : [ data ];
			var fieldContainer = $elem.closest('.field-block > .to-scroll');
			$.each( data, function(){
			    settings.jira.buildSubForms( this, $elem );
			});
			$elem.closest('.field').remove();
		},

		buildSubForms: function( objs, $elem ){
			var container = settings.jira.addIssueType( $elem );
			$.each( Object.keys(objs), function(){
				container.find('[key=' + this + ']').val( objs[this] );
			});
		},

		addIssueType: function( $elem ){
			$elem = $elem ? $elem : this;
			var $template = $($elem.closest('.to-save').find('#issue_type').html());
			var fieldContainer = $elem.closest('.field-block').find('.to-scroll');
			return $template.clone().appendTo(fieldContainer);

		},

	},

	save: function(){
		katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, katana.toJSON(), function( data ) {
			console.log('saved', data);
		});
	},
};
