var cmdBuilder ={

  cmdOptionsViewer: {
    icon_num : 1,
    activeDialog: '',
    activeForm: '',

    init: function(){
      cmdBuilder.cmdOptionsViewer.displayIcons(cmdBuilder.cmdOptionsViewer.icon_num);
    },

    moveIconsRight: function(){
      cmdBuilder.cmdOptionsViewer.displayIcons(cmdBuilder.cmdOptionsViewer.icon_num += 4);
    },
    moveIconsLeft: function(){
      cmdBuilder.cmdOptionsViewer.displayIcons(cmdBuilder.cmdOptionsViewer.icon_num += -4);
    },
    displayIcons: function(n){
      var icons = katana.$activeTab.find(".execution.cmd-icons").children();
      var reduction_val =  (icons.length %2 == 0) ? 1 : 0
      if (n > icons.length) {cmdBuilder.cmdOptionsViewer.icon_num = 1;}
      if (n < 1) {cmdBuilder.cmdOptionsViewer.icon_num = icons.length - reduction_val;}
      for(i=0; i < icons.length; i++) {
        $(icons[i]).hide();
      }
      $(icons[cmdBuilder.cmdOptionsViewer.icon_num-1]).show();
      $(icons[cmdBuilder.cmdOptionsViewer.icon_num]).show();
      $(icons[cmdBuilder.cmdOptionsViewer.icon_num+1]).show();
      $(icons[cmdBuilder.cmdOptionsViewer.icon_num+2]).show();
    },

    openCmdOptionsDialog: function(){
      var cmdOptionsDialog = katana.$activeTab.find('#cmd-options-dialog');
      cmdBuilder.cmdOptionsViewer.showHideDialog(cmdOptionsDialog, 'show');
    },
    closeCmdOptionsDialog: function(){
      var cmdOptionsDialog = katana.$activeTab.find('#cmd-options-dialog');
      cmdBuilder.cmdOptionsViewer.showHideDialog(cmdOptionsDialog, 'hide');
  	},
    // showOptions: function(){
    //   // to be removed
    //   var elem = $(this);
    //   var toShow = katana.$activeTab.find('#' + elem.attr('data-showId'));
    //   var form = toShow.find('form');
    //   cmdBuilder.cmdOptionsViewer.showHideDialog(toShow, 'show', form);
    // },
    openOptionsForm: function(){
      var elem = $(this);
      var closest_dialog = katana.$activeTab.find('#cmd-options-dialog');
      var form = closest_dialog.find('#' + elem.attr('data-showId'));
      cmdBuilder.cmdOptionsViewer.hideAllQnForms();
      cmdBuilder.cmdOptionsViewer.showHideQnForm(form, 'show');



    },
    // closeActiveOptionsForm: function(){
    //   var elem = $(this);
    //   var form = elem.closest('form');
    //   cmdBuilder.cmdOptionsViewer.showHideQnForm(form, 'hide');
    // },
    hideAllQnForms: function(){
      var formsContainer = katana.$activeTab.find('#cmd-options-dialog');
      var formList = formsContainer.find('form');
      $.each(formList, function(index, form){
        $(form).hide();
      });

    },
    showHideQnForm: function(form, val, initForm){
      var panel_container = katana.$activeTab.find('.execution.exec-container')
      if(!initForm){
        var initForm = true;
      }
      if (val == 'hide'){
        form.hide();
        cmdBuilder.cmdOptionsViewer.activeForm = '';
      }
      else {
        // execution.resetForm(form);
        if(form) {
          if(initForm){
            questionaire.init(form);
            form.data('questionaireObject', questionaire);
            questionaire.showQuestion(0);
          }
          form.show();
          cmdBuilder.cmdOptionsViewer.activeForm = form;
        }
      }
      },
    showHideDialog: function(dialog, val, form){
      var panel_container = katana.$activeTab.find('.execution.exec-container')
      if (val == 'hide'){
        panel_container.removeClass('is-blurred');
        panel_container.css('pointer-events', 'auto');
        dialog.hide();
        cmdBuilder.cmdOptionsViewer.activeDialog = '';
      }
      else {
        panel_container.addClass('is-blurred');
        panel_container.css('pointer-events', 'none');
        dialog.show();
        // dialog.data('cmdObject', cmdBuilder.cmdCreator);
        // execution.resetForm(form);
        if(form) {questionaire.init(form);}
        cmdBuilder.cmdOptionsViewer.activeDialog = dialog;
      }
      },



    },


      //  creates the command string based on the individual options selected from UI
      cmdCreator: {

        currentCmd: '',
        cmdArray: [],

        updateCmdObject: function(rxItem){
          // iterate over the command object and see if the item already exists
          var cmdObject = $(this)[0];
          var rxItemName = Object.keys(rxItem)[0];
          var rxItemCmd = rxItem[rxItemName];
          var updated = 0;
          $.each(cmdObject.cmdArray, function(index, item){
            if (rxItemName in item){
              item[rxItemName] = rxItemCmd;
              updated += 1
            }
          });

          // if the recieved item does not exist already add it to the cmd Array
          if (updated ===0){
            cmdObject.cmdArray.push(rxItem);
          };

        },
        clearCmdObject: function(){
          var cmdObject = $(this)[0];
          cmdObject.cmdArray = [];
        },
        formCmdString: function(fileList){
          var cmdObject = $(this)[0];
          cmdString = '';
          var fileString = fileList.join(' ');
          var cmdArray = cmdObject.cmdArray;

          $.each(cmdArray, function(index, optionArray){
            optionName = Object.keys(optionArray)[0];
            optionCmd = optionArray[ optionName];
            if (optionName === 'customOptions'){
              if(optionCmd){
                cmdString = optionCmd + " ";
                return false;
              }
            }else{
              cmdString += optionCmd + " ";
            }

          });
          cmdObject.currentCmd = cmdString + ' ' + fileString;
        },

        getCmd: function(fileList){
          var cmdObject = $(this)[0];
          cmdObject.formCmdString(fileList);
          return cmdObject.currentCmd;
        },
      },

      cmdOptions:{
        submitJiraOptions: function(){
          var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
          var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
          var qnObject = katana.$activeTab.find('#jira-options-form').data('questionaireObject');
          jiraCmdObject = {'jiraOptions': ''};
          jiraCmd='';
          var jira_ad_radio = katana.$activeTab.find("#jira-ad-yes");
          var jira_id_radio = katana.$activeTab.find("#jira-id-yes");
          var jira_proj = katana.$activeTab.find("#jira-project-value");
          var jira_proj_val = katana.$activeTab.find("#jira-project-value").val();
          var jira_id_val = katana.$activeTab.find("#jira-id-value").val();

          
          // check if jira ad is checked
          if ($(jira_ad_radio).is(':checked')){
            jiraCmd += '-ad' + ' ' + '-jiraproj' + ' ' + jira_proj_val;
          }else{
            // check if jirid is checked, if yes get jira id value
            if($(jira_id_radio).is(':checked')){
              jiraCmd += '-jiraid' + ' ' + jira_id_val + ' ' + '-jiraproj' + ' ' + jira_proj_val;
            }
          }
          jiraCmdObject['jiraOptions'] = jiraCmd;
          cmdCreatorObject.updateCmdObject(jiraCmdObject);
          qnObject.form.hide();
          },

        submitCaseOptions: function(){
          var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
          var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
          var qnObject = katana.$activeTab.find('#case-options-form').data('questionaireObject');
          cmdObject = {'caseOptions': ''};
          cmd='';
          var case_ruf_radio = katana.$activeTab.find("#case-ruf");
          var case_rmt_radio = katana.$activeTab.find("#case-rmt");
          var case_seq_radio = katana.$activeTab.find("#case-sequence");
          var case_par_radio = katana.$activeTab.find("#case-parallel");
          var kw_seq_radio = katana.$activeTab.find("#kw-sequence");
          var kw_par_radio = katana.$activeTab.find("#kw-parallel");
          var case_ruf_val = katana.$activeTab.find("#case-ruf-value").val();
          var case_rmt_val = katana.$activeTab.find("#case-rmt-value").val();

          // check if jira ad is checked
          if ($(case_ruf_radio).is(':checked')){
            cmd += '-RUF' + ' ' + case_ruf_val;
          }else if($(case_rmt_radio).is(':checked')){
            cmd += '-RMT' + ' ' + case_rmt_val;
          }else if($(case_seq_radio).is(':checked') & $(kw_seq_radio).is(':checked')){
            cmd += '-tcsequential' + ' ' + '-kwsequential' + '';
          }else if($(case_seq_radio).is(':checked') & $(kw_par_radio).is(':checked')){
            cmd += '-tcsequential' + ' ' + '-kwparallel' + '';
          }else if($(case_par_radio).is(':checked') & $(kw_seq_radio).is(':checked')){
            cmd += '-tcparallel' + ' ' + '-kwsequential' + '';
          }else if($(case_par_radio).is(':checked') & $(kw_par_radio).is(':checked')){
            cmd += '-tcparallel' + ' ' + '-kwparallel' + ' ';
          }
          cmdObject['caseOptions'] = cmd;
          cmdCreatorObject.updateCmdObject(cmdObject);
          qnObject.form.hide();
          },
        submitDataBaseOptions: function(){
          var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
          var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
          var qnObject = katana.$activeTab.find('#dataBase-options-form').data('questionaireObject');

          var status = cmdBuilder.cmdOptions.validateDataBaseOptions(qnObject.form);
          if(status){
            cmdObject = {'dataBaseOptions': ''};
            cmd='';
            var db_val = katana.$activeTab.find("#db-value").val();

            // check if jira ad is checked
            if (db_val){
              cmd += '-dbsystem' + ' ' + db_val;
            }
            cmdObject['dataBaseOptions'] = cmd;
            cmdCreatorObject.updateCmdObject(cmdObject);
            qnObject.form.hide();
            }

          },
        submitSchedulingOptions: function(){
          var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
          var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
          var qnObject = katana.$activeTab.find('#schedule-options-form').data('questionaireObject');

          var status = cmdBuilder.cmdOptions.validateSchedulingOptions(qnObject.form);
          if(status){
              cmdObject = {'schedulingOptions': ''};
              cmd='';
              var date_val = katana.$activeTab.find("#schedule-date-value").val();
              var time_val = katana.$activeTab.find("#schedule-time-value").val();
              var date_time = (date_val + '-' + time_val).replace(/-/g, '\-');
              // check if jira ad is checked
              if (date_time){
                cmd += '-schedule' + ' ' + date_time;
              }
              cmdObject['schedulingOptions'] = cmd;
              cmdCreatorObject.updateCmdObject(cmdObject);
              qnObject.form.hide();
            }
          },
        submitCustomOptions: function(form){
          var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
          var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
          var qnObject = katana.$activeTab.find('#custom-options-form').data('questionaireObject');

          var customCmd = katana.$activeTab.find('#custom-options-value').val();
          cmdObject = {'customOptions': customCmd};
          // cmdBuilder.cmdCreator.clearCmdObject();
          cmdCreatorObject.updateCmdObject(cmdObject);
          qnObject.form.hide();
          },
        vaidateJiraAdNext: function(form){
          var status = true;
          var ad_yes_radio = form.find('#jira-ad-yes');
          var ad_no_radio =  form.find('#jira-ad-no');
          var jira_proj_value = form.find('#jira-project-value');
          var jira_proj_label = katana.$activeTab.find("label[for='jira-project-value']").text();
          btnValid = cmdBuilder.cmdOptions.validateRadioBtns([ad_yes_radio, ad_no_radio]);
          if(!btnValid){cmdBuilder.cmdOptions.alertNoSelection();}
          resultArray = cmdBuilder.cmdOptions.validateTextNotEmpty([jira_proj_value]);
          if(! resultArray['status']){setTimeout(function(){
            cmdBuilder.cmdOptions.alertTextMissing(resultArray['failedList']);
            }, 250);
          }
          status = status &  btnValid & resultArray['status'];
          return status;
        },
        vaidateJiraIdNext: function(form){
          var status = true;
          var id_yes_radio = form.find('#jira-id-yes');
          var id_no_radio =  form.find('#jira-id-no');
          var jira_proj_value = form.find('#jira-project-value');
          var jira_id_value = form.find('#jira-id-value');

          btnValid = cmdBuilder.cmdOptions.validateRadioBtns([id_yes_radio, id_no_radio]);
          if(!btnValid){cmdBuilder.cmdOptions.alertNoSelection();}
          resultArray = cmdBuilder.cmdOptions.validateTextNotEmpty([jira_proj_value, jira_id_value]);
          if(! resultArray['status']){setTimeout(function(){
            cmdBuilder.cmdOptions.alertTextMissing(resultArray['failedList']);
            }, 250);
          }
          status = status &  btnValid & resultArray['status'];
          return status;
        },

        validateCaseOnceMulti: function(form){
          var status = true;
          var once_radio = form.find('#case-once');
          var multi_radio =  form.find('#case-multi');
          status &= cmdBuilder.cmdOptions.validateRadioBtns([once_radio, multi_radio]);
          if(! status){cmdBuilder.cmdOptions.alertNoSelection();}
          return status;
        },
        validateMultiMode: function(form){
          var status = true;
          var btn1 = form.find('#case-ruf');
          var btn2 =  form.find('#case-rmt');
          var text1 = form.find('#case-rmt-value');
          var text2 = form.find('#case-ruf-value');

          btnValid = cmdBuilder.cmdOptions.validateRadioBtns([btn1, btn2]);
          if(! btnValid){cmdBuilder.cmdOptions.alertNoSelection();}
          resultArray = cmdBuilder.cmdOptions.validateTextNotEmpty([text1, text2]);
          if(! resultArray['status']){setTimeout(function(){
            cmdBuilder.cmdOptions.alertTextMissing(resultArray['failedList']);
            }, 250);
          }
          status = status &  btnValid & resultArray['status'];
          return status;

        },
        validateCaseMode: function(form){
          var status = true;
          var btn1 = form.find('#case-sequence');
          var btn2 =  form.find('#case-parallel');
          status &= cmdBuilder.cmdOptions.validateRadioBtns([btn1, btn2]);
          if(! status){cmdBuilder.cmdOptions.alertNoSelection();}
          return status;
        },
        validateKwMode: function(form){
          var status = true;
          var btn1 = form.find('#kw-sequence');
          var btn2 =  form.find('#kw-parallel');
          status &= cmdBuilder.cmdOptions.validateRadioBtns([btn1, btn2]);
          if(! status){cmdBuilder.cmdOptions.alertNoSelection();}
          return status;
        },
        validateDataBaseOptions: function(form){
          var status = true;
          var txt1 = form.find('#db-value');
          resultArray = cmdBuilder.cmdOptions.validateTextNotEmpty([txt1]);
          if(! resultArray['status']){setTimeout(function(){
            cmdBuilder.cmdOptions.alertTextMissing(resultArray['failedList']);
            }, 250);
          }
          return resultArray['status'];
        },
        validateSchedulingOptions: function(form){
          var status = true;
          var txt1 = form.find('#schedule-date-value');
          var txt2 = form.find('#schedule-time-value');

          resultArray = cmdBuilder.cmdOptions.validateTextNotEmpty([txt1, txt2]);
          if(! resultArray['status']){setTimeout(function(){
            cmdBuilder.cmdOptions.alertTextMissing(resultArray['failedList']);
            }, 250);
          }
          return resultArray['status'];
        },
        validateRadioBtns: function(radioBtnList){
          // raise an alert if atleast on of the radio button is not selected.
          var status = false;
          $.each(radioBtnList, function(index, item){
            var result = item.is(':checked')
            status = status || result
          });
          return status
        },

        validateTextNotEmpty: function(textFieldList){
          // raise an alert if the text field is empty
          var status = true;
          var returnArray = {};
          failedList = [];
          $.each(textFieldList, function(index, item){
            if (item.is(':visible') & !item.val()){
              item.addClass('empty');
              status &= false
              failedList.push(item);
            }else{
              item.removeClass('empty');
              status &= true;
            }
          });
          returnArray['status'] = status;
          returnArray['failedList'] = failedList;
          return returnArray;
        },
        alertNoSelection: function(){
          katana.openAlert({'alert_type': 'warning',
                            'heading': 'Warning!',
                            'text': 'Select atleast one option',
                            }
                          );
        },
        alertTextMissing: function(textElementList){
          labelList = [];
          $.each(textElementList, function(index, item){
            itemLabel = katana.$activeTab.find("label[for='"+item.attr('id')+"']").html();
            labelList.push(itemLabel);
          });
          katana.openAlert({'alert_type': 'warning',
                            'heading': 'Warning!',
                            'text': 'Enter values for: '+labelList.join(','),
                            }
                          );
        },
        clearOptions: function(form){
          var name = form.attr('name');
          var cmdBuilderElement = katana.$activeTab.find("#cmd-options-dialog");
          var cmdCreatorObject = cmdBuilderElement.data('cmdCreatorObject');
          cmdObject = {};
          cmdObject[name] = ""
          cmdCreatorObject.updateCmdObject(cmdObject);
        }

    },

//ends
};
