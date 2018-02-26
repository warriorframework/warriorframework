var katana = {
  staticContent: 10,
  $activeTab: null,
  $view: 'null',
  $prevTab: null,

  initApp: function() {
    katana.loadView();
    katana.setActiveTab();
  },

  loadView: function() {
    katana.setView();
    katana.initEventHandlers();
  },

  setView: function() {
    katana.$view = $(document.body).find('.activeView');
  },

  setActiveTab: function() {
    katana.$activeTab = $(document.body).find('.page');
  },

  initEventHandlers: function() {
    katana.$view.on('click', '[katana-click]', function(e) {
      $elem = $(this);
      e.stopPropagation();
      var toCall = $elem.attr('katana-click').replace(/\(.*?\)/, '');
      katana.methodCaller(toCall, $elem);
    });
    katana.$view.on('contextmenu', '[katana-rclick]', function(e) {
      $elem = $(this);
      e.stopPropagation();
      e.preventDefault();
      var toCall = $elem.attr('katana-rclick').replace(/\(.*?\)/, '');
      katana.methodCaller(toCall, $elem, e);
    });
    katana.$view.on('change', '[katana-change]', function(e) {
      $elem = $(this);
      e.stopPropagation();
      var toCall = $elem.attr('katana-change').replace(/\(.*?\)/, '');
      katana.methodCaller(toCall, $elem);
    });
  },

  getObj: function(objString, itter, obj) {
    var objs = objString.split('.');
    var obj = obj ? obj[objs[itter]] : window[objs[itter]];
    itter++;
    if (typeof obj == 'function')
      return obj;
    else if (typeof obj == 'object')
      return katana.getObj(objString, itter, obj);
    else
      return katana.methodExeption;
  },

  methodCaller: function(toCall, $elem, prevElem) {
    var func = katana.getObj(toCall, 0);
    if (func == katana.methodExeption)
      prevElem = toCall;
    func.call($elem, prevElem);
  },

  methodExeption: function(funcName) {
    console.log('Exeption unhandled function', $(this), funcName);
  },

  openTab: function(uid, callBack) {
    var uid = uid ? uid : this.attr('uid') ? this.attr('uid') : false;

    if (uid) {
      var newTab = $($('#blankPage').html()).insertAfter(katana.$activeTab);
      uid = (this && this.hasClass('tab') ? this.find('span').text() : uid).replace(/ /g, '');
      var count = '-' + ($('[uid^=' + uid + ']').length + 1);
      uid = uid + count;
      newTab.attr('id', uid);
      var temp = katana.$view.find('.nav .tab').first();
      var created = temp.clone().insertAfter(temp);
      created.attr('uid', uid).append('<i class="fa fa-times" katana-click="katana.closeTab"></i>');
      created.find('span').text(uid);
      katana.switchTab.call(created, uid);
      callBack && callBack(newTab.find('.page-content-inner'), created);
    }
  },

  subApp: function(uid, callBack) {
    var uid = uid ? uid : this.attr('uid') ? this.attr('uid') : false;
    if (uid) {
      if (katana.$activeTab.find('.page').length != 0)
        var prependTo = katana.$activeTab.find('.page');
      else
        var prependTo = katana.$activeTab;

      var subApp = $($('#' + uid).html()).prependTo(prependTo);
      callBack && callBack(subApp.find('.page-content-inner'));
    }
  },

  closeSubApp: function() {
    var page = katana.$activeTab.find('.page:last');
    page.addClass('removing');
    setTimeout(function() {
      page.remove();
      katana.$activeTab.find('.tab-template').length && katana.tabMod(katana.$view.find('.nav .tab.active'), katana.$activeTab.find('.tab-template'));
    }, 200);
  },

  tabAdded: function(activeTab, prevElem) {
    katana.refreshAutoInit(activeTab, prevElem);
    katana.$view.trigger('tabAdded');
  },

  subAppAdded: function(activeTab, prevElem) {
    katana.refreshAutoInit(activeTab, prevElem);
    katana.$view.trigger('subAppAdded');
  },

  refreshLandingPage: function() {
    var $landingPage = katana.$view.find('#launchpad .page-content');
    $.ajax({
      type: 'GET',
      url: 'refresh_landing_page/',
    }).done(function(data) {
      $landingPage.html(data);
    });
  },

  refreshAutoInit: function(activeTab, prevElem) {
    var autoInit = activeTab.find('[auto-init]');
    autoInit = activeTab.attr('auto-init') ? autoInit.add(activeTab) : autoInit;
    autoInit.each(function() {
      $elem = $(this);
      katana.methodCaller($elem.attr('auto-init').replace('@', ''), $elem, prevElem);
    });
  },

  switchTab: function(uid) {
    var $elem = this != katana ? this : katana.$view.find('.nav .tab:first');
    var uid = uid ? uid : $elem.attr('uid');
    katana.$activeTab.addClass('hidden');
    $elem.siblings().removeClass('active');
    $elem.addClass('active');
    katana.$activeTab = katana.$view.find('#' + uid).removeClass('hidden');
  },

  closeTab: function(ignore) {
    var tab = this.closest('.tab');
    if (tab.hasClass('active') && !ignore)
      katana.switchTab();
    katana.$view.find('#' + tab.attr('uid')).remove();
    tab.remove();
  },

  closePocketFields: function() {
    var $elem = this.closest('.pocket-fields');
    $elem.find('input:first').trigger('change');
    $elem.remove();
  },

  openDialog: function(data, title, buttons, callBack) {
    var final_title = title ? title : '';
    var final_data = data ? data : '';

    var alert_data = {
      "heading": final_title,
      "text": final_data
    };

    if (buttons) {
      alert_data["accept_btn_text"] = "Confirm";
      alert_data["cancel_btn_text"] = "Cancel";
    } else {
      alert_data["show_accept_btn"] = false;
      alert_data["show_cancel_btn"] = false;
    }

    alert_data["alert_type"] = "light";

    katana.openAlert(alert_data, callBack);
  },

  closeDialog: function(dialog, callBack) {
    dialog.remove();
    callBack && callBack();
  },

  popupController: {
    body: '',
    template: $('<div class="popup"><div class="navbar"><div class="title"></div><div class="min"></div><div class="close"></div></div><div class="page-content"></div></div>'),
    tabTemplate: $('<div class="popup-tab-bar"><div class="tab"></div></div>'),

    open: function(content, title, callBack, size) {
      this.body = katana.$view;
      var popup = this.template.clone().appendTo(katana.popupController.body.find('#wui-popups'));
      content && popup.find('.page-content').append(content);
      size && popup.addClass(size);
      katana.popupController.initEvents(popup);
      katana.popupController.createTab(popup);
      title && katana.popupController.setTitle(popup, title);
      callBack && callBack(popup);
      return popup;
    },

    setTitle: function(popup, title) {
      popup.find('.title').text(title);
      popup.data('tabIndex').text(title);
    },

    createTab: function(popup) {
      if (!katana.popupController.tabBar) {
        katana.popupController.tabBar = katana.popupController.tabTemplate.clone().appendTo(katana.popupController.body.find('#wui-popup-nav'));
        katana.popupController.tabBar.find('.tab').remove();
      }
      var tab = katana.popupController.tabTemplate.find('.tab').first().clone().appendTo(katana.popupController.tabBar);
      popup.data('tabIndex', tab);
      tab.on('click', function() {
        katana.popupController.openWindow(popup);
      });
    },

    openWindow: function(popup) {
      var activePopup = katana.popupController.body.find('#wui-popups').find('.popup.active');
      if (activePopup.get(0) !== popup.get(0)) {
        activePopup.removeClass('active');
        popup.removeClass('removeing hidden').addClass('active');
      }
      activePopup = katana.popupController.body.find('#wui-popups').find('.popup.active').detach();
      katana.popupController.body.find('#wui-popups').append(activePopup);
    },

    close: function(popup) {
      popup.data('tabIndex').remove();
      popup.addClass('removeing');
      setTimeout(function() {
        popup.remove();
      }, 300);
    },

    updateActiveWindow: function(popup) {
      var activePopup = katana.popupController.body.find('#wui-popups').find('.popup.active');
      if (activePopup.get(0) !== popup.get(0)) {
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

  translate: function(url, container) {
    $.ajaxSetup({
      async: false
    });
    $.getJSON(url, function(jsonObj) {
      $.each(jsonObj.data, function() {
        var $elem = container.find('input[key="' + this.key + '"], select[key="' + this.key + '"]');
        if ($elem.length > 0) {
          var field = $elem.parent();
          $elem.attr('placeholder', this.translateTo);
          $elem.attr('title', this.toolTip);
          this.data && $elem.data(this.data);
          this.cssClass && field.addClass(this.cssClass);
          this.required && field.addClass('required');
          field.find('> label') && field.find('> label').text(this.translateTo);
        }
      });

    });
  },

  rcPanel: function(event) {
    katana.$view.find('.rc-menu.active').remove();
    var rcMenu = this.closest('.rc-container').find('.rc-menu');
    rcMenu = rcMenu.clone().appendTo(this);
    rcMenu.css({
      'left': event.clientX,
      'top': event.clientY
    }).addClass('active');
    $(window).one('click contextmenu scroll resize', function() {
      katana.$view.find('.rc-menu.active').remove();
    });
  },

  editOrder: function() {
    var tabContainer = this.closest('.tabs');
    katana.$view.addClass('edit-mode');
    tabContainer.sortable({
      items: "div:not(.complete)"
    });
    tabContainer.sortable("option", "disabled", false);
    tabContainer.append('<div class="complete fa fa-check" katana-click="katana.finishOrder"></div>');
    katana.$view.find('.rc-menu.active').remove();
  },


  finishOrder: function() {
    var tabContainer = this.closest('.tabs');
    katana.$view.removeClass('edit-mode');
    tabContainer.sortable("disable");
    this.remove();
  },

  removeApp: function() {
    this.closest('.tab').remove();
  },
  validationAPI: {
      flag: [],

      init: function( $container ) {
        this.flag = [];
        var validationObj = this;
	$container = $container ? $container : katana.$activeTab;
        $container.find('[validation-check]').each(function() {
          var $elem = $(this);
          if ($elem.closest('.field').hasClass('required') && $elem.val() == '')
      validationObj.flag.push({
        '$elem': $elem,
        'response': 'Required'
      });
          katana.methodCaller($elem.attr('validation-check'), $elem);
        });
        if (this.flag.length == 0)
          return true;
        else
          this.warning();
        return false;
      },

      warning: function() {
        $.each(this.flag, function() {
          var $elem = this.$elem;
          var field = $elem.closest('.field');
          field.find('.invalid').remove();
          field.prepend('<div class="invalid">' + this.response + '</div>');
          this.$elem.one('change', function() {
            field.find('.invalid').remove();
          });
        });
    },

    addFlag: function($elem, response) {
      this.flag.push({
        '$elem': $elem,
        'response': response
      });
    },

    PCV: {
      validateIP: function($elem) {
        if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test($elem.val()))
    			return true;
        else
   				katana.validationAPI.addFlag($elem, 'invalid-ip');
      }
    }
  },
  
  openAlert: function(data, callBack_on_accept, callBack_on_dismiss) {
    /*
	    data = {
	        "alert_type": "primary/secondary/success/danger/warning/info(default)/light/dark",
	        "heading": "This is the heading of the alert.",
	        "sub_heading": "false (by default), This is alert sub-heading",
	        "text": "This is text of the alert.",
	        "timer": "false (by default), 500, 1000, etc",
	        "show_accept_btn": "true (by default), false",
	        "accept_btn_text": "Ok (by default), Save, etc",
	        "show_cancel_btn": "true (by default), false",
	        "cancel_btn_text": "Cancel (by default), No, etc",
	        "prompt": "false (by default), true",
	        "prompt_default": "'' by default"
	    }

	    <div class="overlay">
            <div class="col-sm-5 centered">
                <div class="alert alert-data.alert_type" role="alert">
                    <div class="col" style="float: right;">
                        <i class="fa fa-times" style="float: right;"></i>
                    </div>
                    <h4 class="alert-heading">Heading</h4>
                    <p>Sub-Heading</p>
                    <hr>
                    <p class="mb-0">Text</p>
                    <hr>
                    <div class="col" style="text-align: right;">
                    {% if show_accept_btn %}
                        <button class="btn btn-success">accept_btn_text</button>
                    {% endif %}
                    {% if show_cancel_btn %}
                        <button class="btn btn-danger">cancel_btn_text</button>
                    {% endif %}
                    </div>
                </div>
            </div>
        </div>

	    */

    if (callBack_on_accept == undefined) {
      callBack_on_accept = false;
    }

    if (callBack_on_dismiss == undefined) {
      callBack_on_dismiss = false;
    }

    data = katana.validateAlertData(data, katana.createAlertElement, katana.displayAlert,
      callBack_on_accept, callBack_on_dismiss);

  },

  changeBorderColor: function(borderColor) {
    if (borderColor == undefined) {
      borderColor = "white";
    }
    var $body = $('body');
    var $prompt = $body.find('#alert-box-prompt');
    $prompt.css("border-color", borderColor)
  },

  acceptAlert: function(index, callBack_on_accept) {

    var $body = $('body');
    var $alertElement = $body.find('div .alert-overlay');
    $allAlerts = $alertElement.children();
    $alertToBeDismissed = $alertElement.children('[alert-number="'+ index + '"]');
    var $prompt = $body.find('#alert-box-prompt');

    var inputValue = false;

    if (prompt != undefined) {
      inputValue = $prompt.val()
    }

    if (inputValue == "") {
      katana.changeBorderColor("red");
    } else {

        if($allAlerts.length > 1){
            $alertToBeDismissed.remove();
        } else {
            $alertElement.remove();
        }

      if (callBack_on_accept) {
        if (!inputValue) {
          callBack_on_accept();
        } else {
          callBack_on_accept(inputValue);
        }

      };
    }
  },

  dismissAlert: function(index, callBack_on_dismiss) {
    var $body = $('body');
    $alertElement = $body.find('div .alert-overlay');
    $allAlerts = $alertElement.children();
    $alertToBeDismissed = $alertElement.children('[alert-number="'+ index + '"]');
    if($allAlerts.length > 1){
        $alertToBeDismissed.remove();
    } else {
        $alertElement.remove();
    }

    if (callBack_on_dismiss) {
      callBack_on_dismiss();
    }
  },

  displayAlert: function(data, alert_box, callBack_on_accept, callBack_on_dismiss) {

    var $view = katana.$view;
    var $existingOverlay = $view.find('.alert-overlay');
    var index = 0;
    if($existingOverlay.length > 0){
        var $overlayChildren = $existingOverlay.children();
        var lastIndex = parseInt($($overlayChildren[0]).attr('alert-number'));
        if (lastIndex >= $overlayChildren.length){
            index = lastIndex + 1;
        } else {
            index = $overlayChildren.length;
        }
    }
    var $alertBox = $(alert_box);
    $alertBox.attr('alert-number', index)

    $alertBox.find('#cancel-alert').one('click', function() {
        katana.dismissAlert(index, callBack_on_dismiss);
    });
    $alertBox.find('#cancel-alert-icon').one('click', function() {
        katana.dismissAlert(index, callBack_on_dismiss);
    });
    $alertBox.find('#accept-alert').on('click', function() {
        katana.acceptAlert(index, callBack_on_accept);
    });

    if($existingOverlay.length > 0){
        $alertBox.prependTo($existingOverlay);
    } else {
        $totalAlertBox = $('<div class="alert-overlay"></div>');
        $totalAlertBox.html($alertBox);
        $totalAlertBox.prependTo($view);
    }

    if (data.timer) {
      setTimeout(function() {
        katana.dismissAlert(index, callBack_on_dismiss)
      }, data.timer);
    }

  },

  createAlertElement: function(data, callBack, callBack_on_accept, callBack_on_dismiss) {
    var accept_btn_text = "";

    if (data.show_accept_btn) {
      accept_btn_text = '<button class="btn btn-success" id="accept-alert">' + data.accept_btn_text + '</button>'
    }

    var cancel_btn_text = "";

    if (data.show_cancel_btn) {
      cancel_btn_text = '<button class="btn btn-danger" id="cancel-alert">' + data.cancel_btn_text + '</button>'
    }

    var buttons = "";
    var add_break = "<br>";

    if (data.show_accept_btn || data.show_cancel_btn) {
      buttons = '<hr>' +
        '<div class="col" style="text-align: right;">' +
        accept_btn_text + cancel_btn_text +
        '</div>'

      add_break = "";
    }

    var sub_heading = "";

    if (data.sub_heading) {
      sub_heading = '<p>' + data.sub_heading + '</p>';
    }

    var prompt = "";
    var prompt_default = "";

    if(data.prompt_default){
	     prompt_default = data.prompt_default;
	  }

    if(data.prompt) {
	      prompt = "<div><input id='alert-box-prompt' katana-change='katana.changeBorderColor' value='"+ prompt_default +"'></div>"
	  }

    var $alert_box = '<div class="col-sm-5 centered">' +
      '<div class="alert alert-' + data.alert_type + '" role="alert">' +
      '<div class="col" style="float: right;">' +
      '<i id="cancel-alert-icon" class="fa fa-times" style="float: right;"></i>' +
      '</div>' +
      '<h4 class="alert-heading">' + data.heading + '</h4>' + sub_heading +
      '<hr>' +
      '<p class="mb-0 alert-content">' + data.text + '</p>' + prompt + add_break +
      buttons +
      '</div>' +
      '</div>';

    callBack(data, $alert_box, callBack_on_accept, callBack_on_dismiss);
  },

  validateAlertData: function(data, callBack, secondCallBack, callBack_on_accept, callBack_on_dismiss) {

    var allowed_alert_types = ["primary", "secondary", "success", "danger", "warning",
      "info", "light", "dark"
    ];
    var corresponding_headings = {
      "primary": "Hi There!",
      "secondary": "Hello!",
      "success": "Success!",
      "danger": "Oops!",
      "warning": "Warning!",
      "info": "Heads Up!",
      "light": "Hi There!",
      "dark": "Hello!"
    };

    if (!("alert_type" in data)) {
      data["alert_type"] = "info";
    } else {
      if (allowed_alert_types.includes(data.alert_type.toLowerCase())) {
        data.alert_type = data.alert_type.toLowerCase();
      } else {
        data.alert_type = "info";
      }
    }

    if ("heading" in data) {
      if (!data.heading) {
        data.heading = corresponding_headings[data.alert_type]
      }
    } else {
      data.heading = corresponding_headings[data.alert_type]
    }

    if (!("sub_heading" in data)) {
      data["sub_heading"] = false;
    }

    if (!("text") in data) {
      data["text"] = "";
    }

    if (!("timer") in data) {
      data["timer"] = false;
    }

    if (!("show_accept_btn" in data)) {
      data["show_accept_btn"] = true;
    }

    if (!("accept_btn_text" in data)) {
      data["accept_btn_text"] = "Ok"
    }

    if (!("show_cancel_btn" in data)) {
      data["show_cancel_btn"] = true;
    }

    if (!("cancel_btn_text" in data)) {
      data["cancel_btn_text"] = "Cancel"
    }

    if (!("prompt" in data)) {
      data["prompt"] = false;
    }

    callBack(data, secondCallBack, callBack_on_accept, callBack_on_dismiss);

  },

  toJSON: function() {
    var body = katana.$activeTab.find('.to-save');
    var jsonObj = [];
    body.find('.field-block').each(function() {
      var $elem = $(this);
      var tempObj = {};
      tempObj[$elem.find('[key="@name"]').attr('key')] = $elem.find('[key="@name"]').hasClass('.title') ? $elem.find('[key="@name"]').text() : $elem.find('[key="@name"]').val();
      $elem.find('input[key], select[key]').each(function() {
        var sub$elem = $(this);
        if (!sub$elem.closest('.pocket-fields').length)
          tempObj[sub$elem.attr('key')] = sub$elem.val();
      });
      $elem.find('.pocket-fields').each(function() {
        var sub$elem = $(this);
        var key = sub$elem.attr('key');
        var temp = {};
        sub$elem.find('input, select').each(function() {
          var input = $(this);
          temp[input.attr('key')] = input.val();
        });
        tempObj[key] ? tempObj[key].push(temp) : tempObj[key] = [temp];
      });
      $elem.find('.relative-tool-bar > .bool').each(function() {
        var sub$elem = $(this);
        sub$elem.hasClass('active') ? tempObj[sub$elem.attr('key')] = 'true' : '';
      });
      jsonObj.push(tempObj);
    });
    return JSON.stringify(jsonObj);
  },

  toggleActive: function() {
    var $elem = $(this);
    $elem.toggleClass('active');
  },

  toggleActiveGlobal: function() {
    var $elem = $(this);
    $elem.addClass('active');
    katana.$view.one('click', function() {
      $elem.removeClass('active');
    });
  },

  tabMod: function(tab, tabTemp) {

    var tempUID = 'a12410831987013878091870190';
    tab.attr('uid', tempUID);
    katana.$activeTab.attr('id', tempUID);
    var tabText = tabTemp.text().replace(/ /g, '');
    var tabParent = tab.parent();
    var tabRefrence = tabParent.find('[uid^="' + tabText + '"]');

    if (tabTemp.hasClass('only') && tabRefrence.length > 0) {
      setTimeout(function() {
        katana.closeTab.call(tab, true);
        katana.switchTab.call(tabRefrence, tabRefrence.attr('uid'));
      }, 5);
      return true;
    } else {
      setTimeout(function() {
        var count = tabParent.find('[uid^=' + tabText + ']').length + 1;
        var tabName = tabText + '-' + count;
        while (tabParent.find('[uid=' + tabName + ']').length > 0) {
          count--;
          tabName = tabText + '-' + count;
        }
        katana.$activeTab.attr('id', tabName);
        tab.attr('uid', tabName);
        tab.find('span').text(tabName);
      }, 5);
      return false;
    }
  },

  multiSelect: function($elem, $elemToReplace) {
    $elem = $elem ? $elem : this;
    $elemToReplace = $elemToReplace ? $elemToReplace : $elem.find('.multi-select');
    if ($elem.attr('type') == 'checkbox') {
      var checkStatus = $elem.get(0).checked;
      var input = $elem.parent().parent().closest('.field').find('> input');
      value = checkStatus ? (input.val() + $elem.val() + ', ') : (input.val().replace($elem.val() + ', ', ''));
      console.log('test', checkStatus, value, $elem, input, $elem.val());
      input.val(value);
      $elem.parent().parent().siblings('.dropdown-placeholder').text(value);
    } else {
      $($elem.find('#multi-select').html()).insertAfter($elemToReplace);
      $elemToReplace.attr('type', 'hidden');
    }
  },

  expand: function() {
    var topLevel = this.parent();
    if (topLevel.find('.expanded') && topLevel.find('.expanded') != this) {
      topLevel.find('.expanded').removeClass('expanded');
      this.addClass('expanded');
    }
  },

  openProfile: function() {
    var $elem = this;
    $elem.closest('.active').removeClass('active');
    katana.templateAPI.load.call($elem, null, null, null, 'Profile-Settings', function() {
      katana.templateAPI.subAppLoad('/katana/settings/profile_setting_handler');
    });
  },

  quickAnimation: function($elem, className, duration) {
    $elem.addClass(className);
    setTimeout(function() {
      $elem.removeClass(className);
    }, duration);
  },

  fileNav: {
    folderTemp: '',
    fileTemp: '',
    dirTemp: '',

    init: function(prevElem) {
      katana.fileNav.fileTemp = this.find('.file').clone();
      katana.fileNav.folderTemp = this.find('.folder').clone();
      katana.fileNav.dirTemp = this.find('.directory li').clone();
      var $elem = this;
      var template = prevElem.attr('template')
      $elem.addClass('fileSystem').attr('template', template);

      katana.fileNav.getFolder(template, 'foldernames', 'none', null, true, function(objs) {
        $elem.find('.fileSystem').data(objs).addClass('loaded');
        katana.fileNav.moveDirectory.call($elem.find('.fileSystem .folder'), 1);
      });
    },

    moveDirectory: function(level) {
      var level = level ? level : parseInt(this.attr('level')) + 1;
      var fileSystem = this.closest('.fileSystem');
      var directory = fileSystem.find('.directory ul');
      var objs = fileSystem.data();
      ////////////////////////////////////////////////////////////////////////will clean up the not's
      fileSystem.find('li').not('.directory').not('.toggleListView').not('.create').remove();
      directory.empty();

      $.each(objs, function(i) {
        var elem = objs[i];
        if (level == elem.level) {
          if (elem.type == "filenames")
            katana.fileNav.fileTemp.clone().appendTo(fileSystem).attr('link', elem.link && elem.link).find('span').text(elem.name);
          else if (elem.type == "foldernames")
            katana.fileNav.folderTemp.clone().insertAfter(fileSystem.find('.directory')).attr('level', elem.level).find('span').text(elem.name);
        }
        if (level > elem.level && elem.type == 'foldernames')
          directory.append(katana.fileNav.dirTemp.clone().attr('level', elem.level).text(elem.name));
      });
    },

    openFolder: function() {
      katana.fileNav.moveDirectory.call(this, (parseInt(this.attr('level')) + 1));
    },

    openFile: function() {

    },

    listViewToggle: function() {
      this.closest('.page').toggleClass('list-view');
    },
    ////////////////////////////////////////////////////////////////getFolder can be optimised to a single server hit, but will requere changes in katana.py
    getFolder: function(dir, type, folder, objs, isFirst, callBack) {
      var folder = folder ? folder : "none";
      var subDir = true;
      var objs = objs ? objs : [{
        type: 'foldernames',
        name: 'home',
        level: 0
      }];
      var level = 1;

      if (isFirst)
        katana.fileNav.getFolder(dir, 'filenames', folder, objs, false, callBack);

      $.get('/' + dir + type + '/' + folder, function(data) {
        data = JSON.parse(data);
        if (data.length > 0 && type == 'foldernames') {
          var index = objs.findIndex(x => x.name == folder);
          level = index != -1 ? objs[index].level + 1 : 1;
          for (var j = 0; data.length > j; j++) {
            objs.push({
              type: type,
              name: data[j],
              level: level
            });

            katana.fileNav.getFolder(dir, 'filenames', data[j], objs, false, callBack);
            katana.fileNav.getFolder(dir, 'foldernames', data[j], objs, false, callBack);
          }
        } else if (data.length > 0) {

          var index = objs.findIndex(x => x.name == folder);
          level = index != -1 ? objs[index].level + 1 : 1;
          for (var j = 0; data.length > j; j++) {
            objs.push({
              type: type,
              name: data[j],
              level: level
            });
          }
        } else if (data.length == 0 && type == 'foldernames') {
          callBack(objs);
        }
      });

    },

  },

  templateAPI: {
    load: function(url, jsURL, limitedStyles, tabTitle, callBack, options) {
      if (!katana.$view.hasClass('edit-mode')) {
        var $elem = this;
        url = url ? url : $elem ? $elem.attr('url') : '';
        tabTitle = tabTitle ? tabTitle : 'Tab';
        if ($elem != katana.templateAPI) {
          var jsURL = jsURL ? jsURL.split(',') : $elem.attr('jsurls').split(',');
          if (jsURL.length > 0) {
            jsURL.pop();
            katana.templateAPI.importJS(jsURL, function() {
              katana.templateAPI.tabRequst($elem, tabTitle, url, limitedStyles, callBack, options);
            });
          } else {
            katana.templateAPI.tabRequst($elem, tabTitle, url, limitedStyles, callBack, options);
          }
        } else
          katana.templateAPI.tabRequst(katana.$activeTab, tabTitle, url, limitedStyles, callBack, options);
      }
    },

    tabRequst: function($elem, tabTitle, url, limitedStyles, callBack, options) {
      options = options ? options : {};
      options['url'] = url;

      katana.openTab.call($elem, tabTitle, function(container, tab) {
        $.ajax(options).done(function(data) {
          container.append(katana.templateAPI.preProcess(data));
          var toClose = container.find('.tab-template').length && katana.tabMod(tab, container.find('.tab-template'));
          if (toClose == false) {
            limitedStyles || container.find('.limited-styles-true').length && container.addClass('limited-styles');
            container.find('.tool-bar') && container.find('.tool-bar').prependTo(container.parent());
            katana.tabAdded(container, this);
            callBack && callBack(container);
          }
        });
      });
    },

    subAppLoad: function(url, limitedStyles, callBack, options) {
      var $elem = this;
      var url = url ? url : $elem.attr('url');
      options = options ? options : {};
      options['url'] = url;

      katana.subApp.call($elem, 'blankPage', function(container) {
        $.ajax(options).done(function(data) {
          container.append(katana.templateAPI.preProcess(data));
          var toClose = container.find('.tab-template').length && katana.tabMod(katana.$view.find('.nav .tab.active'), container.find('.tab-template'));
          if (toClose == false) {
            limitedStyles || container.find('.limited-styles-true').length && container.addClass('limited-styles');
            container.find('.tool-bar') && container.find('.tool-bar').prependTo(container.parent());
            katana.subAppAdded(container, this);
            callBack && callBack(container);
          }
        });
      });
    },

    preProcess: function(data) {
      data = $(data);
      data.find('.translator').length && katana.translate(data.find('.translator').attr('url'), data);
      return data;
    },

    post: function(url, csrf, toSend, callBack, fallBack, callBackData, fallBackData ) {
      var $elem = this && this != katana.templateAPI ? this : katana.$activeTab;
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
        type: "POST",
        data: {
          data: toSend
        }
      }).done(function(data) {
        callBack && callBack(data, callBackData);
      }).fail(function(data) {
        fallBack && fallBack(data, fallBackData);
      });
    },

    get: function({url, csrf, toSend, dataType, callBack, fallBack, callBackData, fallBackData}={}) {

      // intialize values for url, csrf, dataType, toSend
      var $elem = this ? this : katana.$activeTab;
      var toSend = toSend ? toSend : $elem.find('input:not([name="csrfmiddlewaretoken"])').serializeArray();
      var url = url ? url : $elem.attr('get-url');
      var csrf = csrf ? csrf : $elem.find('.csrf-container > input').val();
      var dataType = dataType ? dataType : 'text'

      // setup csrf token in xhr header
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!this.crossDomain)
            xhr.setRequestHeader("X-CSRFToken", csrf);
        }
      });

      // make an ajax get call using the intialized variables,
      // on sucess the data is sent to success cal back function if one was provided
      $.ajax({
        url: url,
        type: "GET",
        dataType: dataType,
        data: {
          data: toSend
        },
      }).done(function(data) {
        callBack && callBack(data, callBackData);
      }).fail(function(data) {
        fallBack && fallBack(data, fallBackData);
      });
    },

    trigger: function(url, callBack) {
      var $elem = this ? this : katana.$activeTab;
      var url = url ? url : $elem.attr('trigger-url');
      $.ajax({
        url: url,
        dataType: 'text'
      }).done(function(data) {
        callBack && callBack(data);
      });
    },

    importJS: function(jsURL, callBack, i) {
      var i = i ? i : 0;
      var url = jsURL[i].trim();
      katana.openedUrls = katana.openedUrls ? katana.openedUrls : [];
      if (katana.openedUrls.indexOf(url) == -1)
        $.getScript(url, function() {
          katana.openedUrls.push(url);
          i++;
          if (jsURL.length > i)
            katana.templateAPI.importJS(jsURL, callBack, i);
          else
            callBack && callBack();
        });
      else {
        i++;
        if (jsURL.length > i)
          katana.templateAPI.importJS(jsURL, callBack, i);
        else
          callBack && callBack();
      }
    },

  },

    jsTreeAPI: {

      createJstree: function($treeElement, jsTreeData){
        /*
          API to create jstee in the specified element.
          $treeElement: Element where the jstree data should be displayed.
          jsTreeData: the contents of the jstree to be displayed.
        */
        var data = { 'core' : { 'data' : jsTreeData }, "plugins" : [ "sort" , "search"], };
        $treeElement.jstree(data);
        $treeElement.jstree().hide_dots();
      },

      createJstreeSearch: function ($treeElement, $searchBoxElement , jsTreeData) {
        /*
          API to create jstee with search in the specified element.
          $treeElement: Element where the jstree data should be displayed.
          $searchBoxElement: Search box element
          jsTreeData: the contents of the jstree to be displayed.
        */
        katana.jsTreeAPI.createJstree($treeElement, jsTreeData);
        var to = false;
        $searchBoxElement.keyup(function () {
          if(to) { clearTimeout(to); }
          to = setTimeout(function () {
            var v = $searchBoxElement.val();
            $treeElement.jstree(true).search(v);
            }, 250);
          });
        },
    },

  fileExplorerAPI: {

    init: function() {
      var $elem = this;
      var input = $elem.parent().find('input');
      katana.fileExplorerAPI.openFileExplorer(null, null, null, null, function(str) {
        input.val(str).trigger('change');
      });
    },

    openFileExplorer: function(heading, start_directory, csrftoken, parent, callBack_on_accept, callBack_on_dismiss) {
      if (!heading || heading === "" || heading === undefined) {
        heading = "Select a file"
      }
      if (start_directory === undefined || start_directory === "") {
        start_directory = false;
      }
      if (!parent || parent === "" || parent === undefined) {
        var $currentPage = katana.$activeTab;
        var $tabContent = $currentPage.find('.page-content-inner');
      } else {
        $tabContent = parent;
      }
      katana.templateAPI.post('get_file_explorer_data/', csrftoken, {
          "start_dir": start_directory
        },
        function(data) {
          var explorer_modal_html = $($('#file-explorer-template').html());
          var $fileExplorerHeading = explorer_modal_html.find('#file-explorer-heading');
          $fileExplorerHeading.text(heading);

          $(explorer_modal_html).prependTo($tabContent);
          var $directoryData = $tabContent.find('#directory-data');
          $directoryData.jstree({
            "core": {
              "data": [data]
            },
            "plugins": ["search", "sort"],
            "sort": function(a, b) {
              var nodeA = this.get_node(a);
              var nodeB = this.get_node(b);
              var lengthA = nodeA.children.length;
              var lengthB = nodeB.children.length;
              if ((lengthA === 0 && lengthB === 0) || (lengthA > 0 && lengthB > 0))
                return this.get_text(a).toLowerCase() > this.get_text(b).toLowerCase() ? 1 : -1;
              else
                return lengthA > lengthB ? -1 : 1;
            }
          });
          $directoryData.jstree().hide_dots();
          $tabContent.find('#explorer-accept').on('click', function() {
            katana.fileExplorerAPI.acceptFileExplorer(callBack_on_accept, parent);
          });
          $tabContent.find('#explorer-dismiss').on('click', function() {
            katana.fileExplorerAPI.dismissFileExplorer(callBack_on_dismiss, parent);
          });
          $tabContent.find('#explorer-up').on('click', function() {
            katana.fileExplorerAPI.upFileExplorer(data.li_attr["data-path"], csrftoken, parent);
          });

        })
    },

    acceptFileExplorer: function(callBack, parent) {
      if (!parent || parent === "" || parent === undefined) {
        var $currentPage = katana.$activeTab;
      } else {
        $currentPage = parent;
      }
      var $fileExplorerElement = $currentPage.find('div[class="overlay"]');
      var $selectedValue = $fileExplorerElement.find('[aria-selected=true]');
      var data_path = $selectedValue.attr("data-path");
      if (data_path === undefined) {
        alert("Nothing selected");
        return;
      }
      $fileExplorerElement.remove();
      callBack && callBack(data_path);
    },

    dismissFileExplorer: function(callBack, parent) {
      if (!parent || parent === "" || parent === undefined) {
        var $currentPage = katana.$activeTab;
      } else {
        $currentPage = parent;
      }
      var $fileExplorerElement = $currentPage.find('div[class="overlay"]');
      $fileExplorerElement.remove();
      callBack && callBack();
    },

    upFileExplorer: function(currentPath, csrftoken, parent) {
      if (!parent || parent === undefined || parent === "") {
        var $currentPage = katana.$activeTab;
        var $tabContent = $currentPage.find('.page-content-inner');
      } else {
        $tabContent = parent;
      }
      katana.templateAPI.post('get_file_explorer_data/', csrftoken, {
          "path": currentPath
        },
        function(data) {

          var $directoryDataDiv = $tabContent.find('.directory-data-div');
          $directoryDataDiv.html("");
          $directoryDataDiv.append("<div id='directory-data' class='full-size'></div>");
          var $directoryData = $currentPage.find('#directory-data');
          $directoryData.jstree({
            "core": {
              "data": [data]
            },
            "plugins": ["search", "sort"],
            "sort": function(a, b) {
              var nodeA = this.get_node(a);
              var nodeB = this.get_node(b);
              var lengthA = nodeA.children.length;
              var lengthB = nodeB.children.length;
              if ((lengthA === 0 && lengthB === 0) || (lengthA > 0 && lengthB > 0))
                return this.get_text(a).toLowerCase() > this.get_text(b).toLowerCase() ? 1 : -1;
              else
                return lengthA > lengthB ? -1 : 1;
            }
          });
          $directoryData.jstree().hide_dots();
          $tabContent.find('#explorer-up').off('click');
          $tabContent.find('#explorer-up').on('click', function() {
            katana.fileExplorerAPI.upFileExplorer(data.li_attr["data-path"], csrftoken, parent);
          });
        });
    },

  },

};
