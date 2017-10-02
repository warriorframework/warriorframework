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
			this.find('[key="lastName"], [key="firstName"]').closest('.field').insertAfter( this.find('.profile-image:last') );
		},

		selectProfileImage: function(){
			var $elem = this;
			$elem.parent().find('input').click();
		},

		encodeImage: function(){
			var $elem = this;
			var element = this.get(0);
			var toplevel = $elem.parent();
			var file = element.files[0];
			var preview = toplevel.find('.image');
			var reader = new FileReader();
			preview.addClass('loading');
			reader.onloadend = function() {
			 var result = reader.result;
			 toplevel.find('input[name="image"]').val(result);
			 preview.css('background-image', 'url(' + result + ')');
			 preview.removeClass('loading');
			}
			reader.readAsDataURL(file);
		},

		save: function(){
			settings.save.call(this);
			var bgImage = this.closest('.page').find('input[key="bgImage"]').val() ? this.closest('.page').find('input[key="bgImage"]').val() : '';
			var profileImage = this.closest('.page').find('input[key="Base64image"]').val() ? this.closest('.page').find('input[key="Base64image"]').val() : '';
		  if(bgImage != "")
				$('#bg-style').html('.page{ background-image: url(' + bgImage + ')}');
			else
		 		$('#bg-style').html('');

		  katana.$view.find('.quick-user .profile-image').css('background-image', 'url(' + profileImage + ')');
		},

		clearImage: function(){
			var topLevel = this.closest('.profile-image');
			topLevel.find('.image').css('background-image', 'none');
			topLevel.find('input').val('');
		}

	},

	mail: {
 		init: function(){
			settings.changeDetection.call( this );
			settings.mail.changeFrequency(this);
		},

		changeFrequency: function( $elem ){
			katana.multiSelect( $elem, $elem.find('[key="@mail_on"]') );
		}
	},

	jira: {
		boolHandler: function( $elem ){
			var button = $elem.closest('.field-block').find('.relative-tool-bar [key="' + $elem.attr('key') + '"]');
			$elem.val() == 'true' && button.addClass('active');
			$elem.closest('.field').remove();
		},

		password: function(){
			this.attr('type', 'password');
		},

		default: function(){
			settings.jira.boolHandler( $(this) );
		},

		append_log: function(){
			settings.jira.boolHandler( $(this) );
		},

		defaultClick: function(){
			this.closest('.page-content').find('[key="@default"]').not( this ).removeClass('active');
			katana.toggleActive.call(this);
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
			$elem == this && fieldContainer.find('input:first').trigger('change');
			return $template.clone().appendTo(fieldContainer);

		},

		deleteBlock: function(){
			var fieldBlock = this.closest('.field-block');
			fieldBlock.find('input').trigger('change');
			fieldBlock.remove();
		},

		addBlock: function(){
			var $elem = this;
			var feildBlock = $elem.closest('.field-block');
			feildBlock.find('input:first').trigger('change');
			feildBlock.clone().insertAfter( feildBlock );
		}
	},

	addSystem: function(){
		var page = this.closest('.page-content');
		var template = $(page.find('#block-template').html()).appendTo(page.find('.to-save'));
		template.find('input:first').trigger('change');
	},

	changeDetection: function(){
		var $elem = this;
		$elem.on('change', 'input, select', function(){
			$elem.closest('.page-content').find('.saved').removeClass('saved');
		});
	},

	save: function(){
		var $elem = this;
		$elem.removeClass('saved').addClass('loading');
		katana.templateAPI.post.call( katana.$activeTab.find('.to-save'), null, null, katana.toJSON(), function( data ) {
			console.log('saved', data);
			$elem.removeClass('loading').addClass('saved');
		});
	},
};
