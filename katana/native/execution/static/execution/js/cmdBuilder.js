var cmdBuilder ={

  cmdOptionsViewer: {
    icon_num : 1,
    activeDialog: '',

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

    showOptions: function(){
      var elem = $(this);
      var toShow = katana.$activeTab.find('#' + elem.attr('data-showId'));
      var form = toShow.find('form');
      cmdBuilder.cmdOptionsViewer.showHideDialog(toShow, 'show', form);
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
        // execution.resetForm(form);
        questionaire.init(form);
        cmdBuilder.cmdOptionsViewer.activeDialog = dialog;
      }
      },

    //   resetFields: function(){
    //     // use this to reset fields on a button click, also resets radio buttons
    //     elem = $(this);
    //     /* By default resets the radio buttons of the given form*/
    //     var form_id = elem.attr('form');
    //     var form = elem.closest('.page-content').find('#'+form_id);
    //     form_parent = form.parent();
    //     radio_btns = form_parent.find("input[type='radio']");
    //     for(i=0; i < radio_btns.length; i++) {
    //       $(radio_btns[i]).prop('checked', false);
    //     }
    //     $(form)[0].reset();
    //     questionaire.clearQnAttr(['data-displayed']);
    //   },
    //


    },


      //  creates the command string based on the individual options selected from UI
      cmdCreator: {

        currentCmd: '',
        cmdArray: [],

        updateCmdObject: function(rxItem){
          // iterate over the command object and see if the item already exists
          var rxItemName = Object.keys(rxItem)[0];
          var rxItemCmd = rxItem[rxItemName];
          var updated = 0;
          $.each(cmdBuilder.cmdCreator.cmdArray, function(index, item){
            if (rxItemName in item){
              item[rxItemName] = rxItemCmd;
              updated += 1
            }
          });

          // if the recieved item does not exist already add it to the cmd Array
          if (updated ===0){
            cmdBuilder.cmdCreator.cmdArray.push(rxItem);
          };
        },
        clearCmdObject: function(){
          cmdBuilder.cmdCreator.cmdArray = [];
        },
        formCmdString: function(fileList){
          cmdString = '';
          var fileString = fileList.join(' ');
          var cmdArray = cmdBuilder.cmdCreator.cmdArray;

          $.each(cmdArray, function(index, item){
            itemCmd = item[ Object.keys(item)[0]];
            cmdString += itemCmd + " ";
          });
          cmdBuilder.cmdCreator.currentCmd = cmdString + ' ' + fileString;
          console.log(cmdBuilder.cmdCreator.currentCmd);
        },

        getCmd: function(fileList){
          cmdBuilder.cmdCreator.formCmdString(fileList);
          return cmdBuilder.cmdCreator.currentCmd;
        },
      },

      cmdOptions:{
        submitJiraOptions: function(){
          jiraCmdObject = {'jiraOptions': ''};
          jiraCmd='';
          var jira_ad_radio = questionaire.form.find("#jira-ad-yes");
          var jira_id_radio = questionaire.form.find("#jira-id-yes");
          var jira_proj_val = questionaire.form.find("#jira-project-value").val();
          var jira_id_val = questionaire.form.find("#jira-id-value").val();

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
          cmdBuilder.cmdCreator.updateCmdObject(jiraCmdObject);
          execution.closeDialog();
          },

        submitCaseOptions: function(){
          cmdObject = {'caseOptions': ''};
          cmd='';
          var case_ruf_radio = questionaire.form.find("#case-ruf");
          var case_rmt_radio = questionaire.form.find("#case-rmt");
          var case_seq_radio = questionaire.form.find("#case-sequence");
          var case_par_radio = questionaire.form.find("#case-parallel");
          var kw_seq_radio = questionaire.form.find("#kw-sequence");
          var kw_par_radio = questionaire.form.find("#kw-parallel");
          var case_ruf_val = questionaire.form.find("#case-ruf-value").val();
          var case_rmt_val = questionaire.form.find("#case-rmt-value").val();

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
            cmd += '-tcparallel' + ' ' + '-kwparallel' + '';
          }
          cmdObject['caseOptions'] = cmd;
          cmdBuilder.cmdCreator.updateCmdObject(cmdObject);
          execution.closeDialog();
          // console.log(cmdObject);
          },
        submitDataBaseOptions: function(){
          var status = cmdBuilder.cmdOptions.validateDataBaseOptions(questionaire.form);
          if(status){
            cmdObject = {'dataBaseOptions': ''};
            cmd='';
            var db_val = questionaire.form.find("#db-value").val();

            // check if jira ad is checked
            if (db_val){
              cmd += '-dbsystem' + ' ' + db_val;
            }
            cmdObject['dataBaseOptions'] = cmd;
            cmdBuilder.cmdCreator.updateCmdObject(cmdObject);
            execution.closeDialog();
            }
          },
        submitSchedulingOptions: function(){
          var status = cmdBuilder.cmdOptions.validateSchedulingOptions(questionaire.form);
          if(status){
              cmdObject = {'schedulingOptions': ''};
              cmd='';
              var date_val = questionaire.form.find("#schedule-date-value").val();
              var time_val = questionaire.form.find("#schedule-time-value").val();
              var date_time = (date_val + '-' + time_val).replace(/-/g, '\-');
              console.log(date_time);
              // check if jira ad is checked
              if (date_time){
                cmd += '-schedule' + ' ' + date_time;
              }
              cmdObject['schedulingOptions'] = cmd;
              cmdBuilder.cmdCreator.updateCmdObject(cmdObject);
              execution.closeDialog();
            }
          },
        submitCustomOptions: function(form){
          var customCmd = questionaire.form.find('#custom-options-value').val();
          cmdObject = {'customOptions': customCmd};
          cmdBuilder.cmdCreator.clearCmdObject();
          cmdBuilder.cmdCreator.updateCmdObject(cmdObject);
          execution.closeDialog();
          },
        vaidateJiraAdNext: function(form){
          var status = true;
          var ad_yes_radio = form.find('#jira-ad-yes');
          var ad_no_radio =  form.find('#jira-ad-no');
          var jira_proj_value = form.find('#jira-project-value');

          btnValid = cmdBuilder.cmdOptions.validateRadioBtns([ad_yes_radio, ad_no_radio]);
          if(!btnValid){alert('select atleast one option');}

          textValid = cmdBuilder.cmdOptions.validateTextNotEmpty([jira_proj_value]);
          if(! textValid){setTimeout(function() { alert("Enter values for highlighted fields"); }, 250);}

          status = status &  btnValid & textValid

          return status;
        },
        vaidateJiraIdNext: function(form){
          var status = true;
          var id_yes_radio = form.find('#jira-id-yes');
          var id_no_radio =  form.find('#jira-id-no');
          var jira_proj_value = form.find('#jira-project-value');
          var jira_id_value = form.find('#jira-id-value');

          btnValid = cmdBuilder.cmdOptions.validateRadioBtns([id_yes_radio, id_no_radio]);
          if(! btnValid){alert('select atleast one option');}
          textValid = cmdBuilder.cmdOptions.validateTextNotEmpty([jira_proj_value, jira_id_value]);
          if(! textValid){setTimeout(function() { alert("Enter values for highlighted fields"); }, 250);}
          status = status &  btnValid & textValid;
          return status;
        },

        validateCaseOnceMulti: function(form){
          var status = true;
          var once_radio = form.find('#case-once');
          var multi_radio =  form.find('#case-multi');
          status &= cmdBuilder.cmdOptions.validateRadioBtns([once_radio, multi_radio]);
          if(! status){alert('select atleast one option');}
          return status;
        },
        validateMultiMode: function(form){
          var status = true;
          var btn1 = form.find('#case-ruf');
          var btn2 =  form.find('#case-rmt');
          var text1 = form.find('#case-rmt-value');
          var text2 = form.find('#case-ruf-value');

          btnValid = cmdBuilder.cmdOptions.validateRadioBtns([btn1, btn2]);
          if(! btnValid){alert('select atleast one option');}
          textValid = cmdBuilder.cmdOptions.validateTextNotEmpty([text1, text2]);
          if(! textValid){setTimeout(function() { alert("Enter values for highlighted fields"); }, 250);}
          status = status &  btnValid & textValid;
          return status;

        },
        validateCaseMode: function(form){
          var status = true;
          var btn1 = form.find('#case-sequence');
          var btn2 =  form.find('#case-parallel');
          status &= cmdBuilder.cmdOptions.validateRadioBtns([btn1, btn2]);
          if(! status){alert('select atleast one option');}
          return status;
        },
        validateKwMode: function(form){
          var status = true;
          var btn1 = form.find('#kw-sequence');
          var btn2 =  form.find('#kw-parallel');
          status &= cmdBuilder.cmdOptions.validateRadioBtns([btn1, btn2]);
          if(! status){alert('select atleast one option');}
          return status;
        },
        validateDataBaseOptions: function(form){
          var status = true;
          var txt1 = form.find('#db-value');
          status &= cmdBuilder.cmdOptions.validateTextNotEmpty([txt1]);
          if(! status){setTimeout(function() { alert("Enter values for highlighted fields"); }, 250);}
          return status;
        },
        validateSchedulingOptions: function(form){
          var status = true;
          var txt1 = form.find('#schedule-date-value');
          var txt2 = form.find('#schedule-time-value');
          status &= cmdBuilder.cmdOptions.validateTextNotEmpty([txt1, txt2]);
          if(! status){setTimeout(function() { alert("Enter values for highlighted fields"); }, 250);}
          return status;
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
          $.each(textFieldList, function(index, item){
            if (item.is(':visible') & !item.val()){
              item.addClass('empty');
              status &= false
            }else{
              item.removeClass('empty');
              status &= true;
            }
          });
          return status
        },


    },

//ends
};
