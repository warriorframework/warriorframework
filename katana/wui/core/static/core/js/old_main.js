var katana = {
	staticContent: 10,
	$activeTab: null,
	$view: 'null',
	$prevTab: null,

	initApp: function(){
		katana.loadView();
		katana.setActiveTab();
	},

	loadView: function(){
		katana.setView();
		katana.initClickHandler();
	},

	setView: function() {
		katana.$view = $( document.body ).find( '.activeView' );
	},

	setActiveTab: function() {
		katana.$activeTab = $( document.body ).find( '.page' );
	},

	initClickHandler: function(){
		katana.$view.on( 'click', '[katana-click]', function( e ){
			$elem = $(this);
			e.stopPropagation();
			var toCall = $elem.attr( 'katana-click' ).replace( /\(.*?\)/, '' );
			katana.methodCaller( toCall, $elem );
		});
	},

	getObj: function( objString, itter, obj ){
		var objs = objString.split('.');
		var obj = obj ? obj[ objs[itter] ] : window[ objs[itter] ];
		itter++;
		if( typeof obj == 'function' )
			return obj;
		else if( typeof obj == 'object' )
			return katana.getObj( objString, itter, obj );
		else
			return katana.methodExeption;
	},

  methodCaller: function( toCall, $elem, prevElem ){
		var func = katana.getObj( toCall, 0 );
		if( func == katana.methodExeption )
			prevElem = toCall;
		func.call( $elem, prevElem );
	},

	methodExeption: function( funcName ){
		console.log( 'Exeption unhandled function', $(this), funcName );
	},

	openTab: function( uid, callBack ){
		var uid = uid ? uid : this.attr('uid') ? this.attr('uid') : false;
		if( uid )
			{
				var newTab = $( $( '#' + uid ).html() ).insertAfter( katana.$activeTab );
				var count = '-' + $('[id^=' + uid + ']' ).length;
				uid = uid + count;
				newTab.attr('id', uid );
				var temp = katana.$view.find('.nav .tab').first();
				var created = temp.clone().insertAfter( temp );
				created.attr( 'uid', uid ).text( this.hasClass('tab') ? this.find('span').text() + count : uid ).append('<i class="fa fa-times" katana-click="katana.closeTab"></i>');
				katana.switchTab.call( created, uid );
				callBack && callBack( newTab.find('.page-content-inner') );
			}
	},

	subApp: function( uid, callBack ){
		var uid = uid ? uid : this.attr('uid') ? this.attr('uid') : false;
		if( uid )
			{
				var subApp = $( $( '#' + uid ).html() ).prependTo( katana.$activeTab );
				callBack && callBack( subApp.find('.page-content-inner') );

			}
	},

	closeSubApp: function(){
		var page = katana.$activeTab.find('.page:first');
		page.addClass('removing');
		setTimeout(function () {
			page.remove();
		}, 200);
	},

	tabAdded: function( activeTab, prevElem ){
		katana.refreshAutoInit( activeTab, prevElem );
	},

	subAppAdded: function( activeTab, prevElem ){
		katana.refreshAutoInit( activeTab, prevElem );
	},

	refreshAutoInit: function( activeTab, prevElem ){
			var autoInit = activeTab.find('[auto-init]');
			autoInit = activeTab.attr('auto-init') ? autoInit.add( activeTab ) : autoInit;
			autoInit.each( function(){
				$elem = $(this);
				katana.methodCaller( $elem.attr('auto-init').replace('@', ''), $elem, prevElem );
			});
		},

	switchTab: function( uid ){
		var $elem = this != katana ? this : katana.$view.find('.nav .tab:first');
		var uid = uid ? uid : $elem.attr( 'uid' );
		katana.$activeTab.addClass('hidden');
		$elem.siblings().removeClass('active');
		$elem.addClass('active');
		katana.$activeTab = katana.$view.find( '#' + uid ).removeClass('hidden');
	},

  closeTab: function(){
		var tab = this.closest('.tab');
		if( tab.hasClass('active') )
			katana.switchTab();
		katana.$view.find( '#' +tab.attr('uid') ).remove();
		tab.remove();
	},

	closePocketFeilds: function(){
		this.closest('.pocket-feilds').remove();
	},

	popupController: {
	  body: '',
	  template: $('<div class="popup"><div class="navbar"><div class="title"></div><div class="min"></div><div class="close"></div></div><div class="page-content"></div></div>'),
	  tabTemplate: $('<div class="popup-tab-bar"><div class="tab"></div></div>'),

	  open: function(content, title, callBack) {
			this.body = katana.$view;
	    var popup = this.template.clone().appendTo(katana.popupController.body);
	    content && popup.find('.page-content').append(content);
	    katana.popupController.initEvents(popup);
	    katana.popupController.createTab(popup);
	    title && katana.popupController.setTitle(popup, title);
			callBack && callBack( popup );
	    return popup;
	  },

	  setTitle: function(popup, title) {
	    popup.find('.title').text(title);
	    popup.data('tabIndex').text(title);
	  },

	  createTab: function(popup) {
	    if (!katana.popupController.tabBar) {
	      katana.popupController.tabBar = katana.popupController.tabTemplate.clone().appendTo(katana.popupController.body);
	      katana.popupController.tabBar.find('.tab').remove();
	    }
	    var tab = katana.popupController.tabTemplate.find('.tab').first().clone().appendTo(katana.popupController.tabBar);
	    popup.data('tabIndex', tab);
	    tab.on('click', function() {
	      katana.popupController.openWindow(popup);
	    });
	  },

	  openWindow: function(popup) {
	    var activePopup = katana.popupController.body.find('.popup.active');
	    if (activePopup.get(0) != popup.get(0)) {
	      activePopup.removeClass('active');
	      popup.removeClass('removeing hidden').addClass('active');
	    }
	  },

	  close: function(popup) {
	    popup.data('tabIndex').remove();
	    popup.addClass('removeing');
	    setTimeout(function() {
	      popup.remove();
	    }, 300);
	  },

	  updateActiveWindow: function(popup) {
	    var activePopup = katana.popupController.body.find('.popup.active');
	    if (activePopup.get(0) != popup.get(0)) {
	      activePopup.removeClass('active');
	      popup.addClass('active');
	    }
	  },

	  min: function(popup) {
	    popup.addClass('removeing');
	    setTimeout(function() {
	      popup.addClass('hidden').removeClass('active');
	    }, 300);
	  },

	  initEvents: function(popup) {
	    var pressed = false;
	    var xoffset = 0;
	    var yoffset = 0;
	    var x, y;
	    var startPointx = 0;
	    var startPointy = 0;
	    var $elem;
	    popup.find('.navbar .title').on('mousedown', function(e) {
	      e.stopPropagation();
	      e.preventDefault();
	      katana.popupController.updateActiveWindow(popup);
	      $elem = $(this).closest('.popup');
	      pressed = true;
	      xoffset = e.pageX;
	      yoffset = e.pageY;
	      $elem.removeClass('leftJustify').removeClass('rightJustify');
	      katana.popupController.body.addClass('no-select');
	      katana.popupController.body.on('mousemove', function(j) {
	        if (pressed) {
	          x = (j.pageX - xoffset + startPointx);
	          y = (j.pageY - yoffset + startPointy);
	          $elem.css('transform', 'translate3d( ' + x + 'px, ' + y + 'px,0 )');
	        }
	      });
	      katana.popupController.body.one('mouseup', function() {
	        katana.popupController.body.off('mousemove');
	        startPointx = x;
	        startPointy = y;
	        pressed = false;
	        katana.popupController.body.removeClass('no-select');
	        if ($elem.offset().left < 0) {
	          $elem.removeClass('rightJustify').addClass('leftJustify');
	          startPointx = 0;
	          startPointy = 0;
	        } else if ($elem.offset().left > $(this).width() - $elem.width()) {
	          $elem.removeClass('leftJustify').addClass('rightJustify');
	          startPoinx = $(this).width() - $elem.width();
	          startPointy = 0;
	        }
	      });
	    });
	    popup.find('.close').one('click', function(e) {
	      katana.popupController.close(popup);
	      e.stopPropagation();
	      e.preventDefault();
	    });
	    popup.on('click', function() {
	      katana.popupController.updateActiveWindow(popup);
	    });
	    popup.find('.min').on('click', function(e) {
	      katana.popupController.min(popup);
	      e.stopPropagation();
	      e.preventDefault();
	    });
	  }

	},
	
	toJSON: function(){
		var body = katana.$activeTab.find('.to-save');
		var jsonObj = [];
		body.find('.feild-block').each( function(){
			var $elem = $(this);
			var tempObj = {};
			tempObj[ $elem.find('[key="@name"]').attr('key') ] = $elem.find('[key="@name"]').text();
			$elem.find('input, select').each( function() {
				var sub$elem = $(this);
				if( !sub$elem.closest('.pocket-feilds').length )
					tempObj[ sub$elem.attr('key') ] = sub$elem.val();
			});
			$elem.find('.pocket-feilds').each( function() {
				var sub$elem = $(this);
				var key = sub$elem.attr('key');
				var temp = {};
				sub$elem.find('input, select').each( function(){
					var input = $(this);
					temp[ input.attr('key') ] = input.val();
				});
			 tempObj[ key ] ? tempObj[ key ].push(temp) : tempObj[ key ] = [temp];
			});
			$elem.find('.relative-tool-bar > .bool').each(function() {
				var sub$elem = $(this);
				sub$elem.hasClass('active') ? tempObj[ sub$elem.attr('key') ] = 'true' : '';
			});
			jsonObj.push(tempObj);
		});
		return JSON.stringify(jsonObj);
	},

	toggleActive: function(){
		var $elem = $(this);
		$elem.toggleClass('active');
	},

	fileNav:{
		folderTemp: '',
		fileTemp: '',
		dirTemp: '',

		init: function( prevElem ){
			katana.fileNav.fileTemp = this.find('.file').clone();
			katana.fileNav.folderTemp = this.find('.folder').clone();
			katana.fileNav.dirTemp = this.find('.directory li').clone();
			var $elem = this;
			var template = prevElem.attr('template')
			$elem.addClass('fileSystem').attr('template', template);

		  katana.fileNav.getFolder( template, 'foldernames', 'none', null, true, function( objs ){
				$elem.find('.fileSystem').data( objs ).addClass('loaded');
				katana.fileNav.moveDirectory.call( $elem.find('.fileSystem .folder'), 1 );
			} );
		},

		moveDirectory: function( level ){
			var level = level ? level : parseInt(this.attr('level')) + 1;
			var fileSystem = this.closest('.fileSystem');
			var directory = fileSystem.find('.directory ul');
			var objs = fileSystem.data();
////////////////////////////////////////////////////////////////////////will clean up the not's
			fileSystem.find('li').not('.directory').not('.toggleListView').not('.create').remove();
			directory.empty();

			$.each( objs, function(i){
					var elem = objs[i];
					if( level == elem.level )
					{
						if( elem.type == "filenames")
							katana.fileNav.fileTemp.clone().appendTo( fileSystem ).attr( 'link', elem.link && elem.link ).find('span').text( elem.name );
						else if( elem.type == "foldernames" )
							katana.fileNav.folderTemp.clone().insertAfter( fileSystem.find('.directory') ).attr( 'level', elem.level ).find('span').text( elem.name );
					}
					if( level > elem.level && elem.type == 'foldernames')
						directory.append( katana.fileNav.dirTemp.clone().attr( 'level', elem.level ).text( elem.name ) );
				});
		},

		openFolder: function(){
			katana.fileNav.moveDirectory.call( this, (parseInt(this.attr('level')) + 1) );
		},

		openFile: function(){


		},

		listViewToggle: function(){
			this.closest('.page').toggleClass('list-view');
		},
////////////////////////////////////////////////////////////////getFolder can be optimised to a single server hit, but will requere changes in katana.py
		getFolder: function( dir, type, folder, objs, isFirst, callBack ){
			var folder = folder ? folder : "none";
			var subDir = true;
			var objs = objs ? objs : [{ type: 'foldernames', name: 'home', level: 0 }];
			var level = 1;

			if( isFirst )
				katana.fileNav.getFolder( dir, 'filenames', folder, objs, false, callBack );

			$.get( '/' + dir + type + '/' + folder, function( data ){
				data = JSON.parse( data );
				if( data.length > 0 && type == 'foldernames' ){
					var index = objs.findIndex( x => x.name == folder );
					level = index != -1 ? objs[index].level + 1 : 1;
					for(var j = 0; data.length > j; j++){
						objs.push({ type: type, name: data[j], level: level });

						katana.fileNav.getFolder( dir, 'filenames', data[j], objs, false, callBack );
						katana.fileNav.getFolder( dir, 'foldernames', data[j], objs, false, callBack );
					}
				}
				else if( data.length > 0 ){

					var index = objs.findIndex( x => x.name == folder );
					level = index != -1 ? objs[index].level + 1 : 1;
					for(var j = 0; data.length > j; j++){
						objs.push({ type: type, name: data[j], level: level });
					}
				}
				else if( data.length == 0 && type == 'foldernames' ){
					callBack( objs );
				}
			});

		},

	},

	templateAPI:{
			load: function( url, jsURL, limitedStyles ){
				var $elem = this;
				var url = url ? url : $elem.attr('url');
				var jsURL = $elem.attr('jsurls').split(',');
				jsURL.pop();
				katana.templateAPI.importJS( jsURL, function(){
					katana.openTab.call( $elem, 'blankPage', function( container ){
						$.ajax({
							url: url,
							dataType: 'text'
						}).done(function( data ) {
							container.append( katana.templateAPI.preProcess( data ) );
							limitedStyles || container.find('.limited-styles-true').length && container.addClass('limited-styles');
							katana.tabAdded( container, this );
						});
					});
				});

			},

			subAppLoad: function( url, limitedStyles ){
				var $elem = this;
				var url = url ? url : $elem.attr('url');

				katana.subApp.call( $elem, 'blankPage', function( container ){
					$.ajax({
						url: url,
						dataType: 'text'
					}).done(function( data ) {
						container.append( katana.templateAPI.preProcess( data ) );
						limitedStyles || container.find('.limited-styles-true').length && container.addClass('limited-styles');
						container.find('.tool-bar') && container.find('.tool-bar').prependTo(container.parent());
						katana.subAppAdded( container, this );
					});
				});
			},

		 preProcess: function( data ){
			 //data = data.replace( /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
			 return data;
		 },

		 post: function( url, csrf, toSend, callBack ){
			 var $elem = this;
			 var toSend = toSend ? toSend : $elem.find('input:not([name="csrfmiddlewaretoken"])').serializeArray();
			 var url = url ? url : $elem.attr('post-url');
			 var csrf = csrf ? csrf : $elem.find('.csrf-container > input').val();

			 $.ajaxSetup({
			    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain)
		        	xhr.setRequestHeader("X-CSRFToken", csrf);
			    }
				});
			 $.ajax({
				 url: url,
				 type : "POST",
				 data : { data: toSend }
			 }).done(function( data ) {
				 callBack && callBack( data );
			 });
		 },

		 trigger: function( url, callBack ){
			 var $elem = this;
			 var url = url ? url : $elem.attr('trigger-url');
			 $.ajax({
				 url: url,
				 dataType: 'text'
			 }).done(function( data ) {
				 callBack && callBack( data );
			 });
		 },

		 importJS: function( jsURL, callBack, i ){
		 	var i = i ? i : 0;
			$.getScript( jsURL[i], function() {
				i++;
				if( jsURL.length > i )
					katana.templateAPI.importJS( jsURL, callBack, i );
				else
					callBack && callBack();
			});
		},

	},
///////////////////////////////////////////Methods named by template

};
