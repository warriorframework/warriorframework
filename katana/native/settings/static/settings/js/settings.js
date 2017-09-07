var settings = {

	closeSetting: function(){
		if( this.parent().find('.saved').length )
			katana.closeSubApp();
		else
			katana.openDialog( 'Are you sure you would like to close this page?', 'Confirm', true, katana.closeSubApp );
	},

	encrypetion: {
		save: function(){
			var $elem = this;
			$elem.addClass('loading');
			katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, null, function( data ){
				console.log('saved', data);
				$elem.removeClass('loading').addClass('saved');
			} );
		}
	},

	profile:{
		init: function(){
			settings.changeDetection.call(this);
			this.find('.profile-image').insertAfter( this.find('.field-block .title'));
		},

		selectProfileImage: function(){
			var $elem = this;
			$elem.parent().find('input').click();
		},

		encodeImage: function(){
			var $elem = this;
			var element = this.get(0);
			var file = element.files[0];
			var reader = new FileReader();
			reader.onloadend = function() {
			 var result = reader.result;
			 var toplevel = $elem.parent();
			 toplevel.find('input[name="image"]').val(result);
			 toplevel.find('.image').css('background-image', 'url(' + result + ')');
			}
			reader.readAsDataURL(file);
		},

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

		deleteBlock: function(){
			this.closest('.field-block').remove();
		},

		addBlock: function(){
			var $elem = this;
			var feildBlock = $elem.closest('.field-block');
			feildBlock.clone().insertAfter( feildBlock );
		}
	},

	changeDetection: function(){
		var $elem = this;
		$elem.on('change', 'input, select', function(){
			$elem.closest('.page-content').find('.saved').removeClass('saved');
		});
	},

	save: function(){
		var $elem = this;
		$elem.addClass('loading');
		katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, katana.toJSON(), function( data ) {
			console.log('saved', data);
			$elem.removeClass('loading').addClass('saved');
		});
	},
};
