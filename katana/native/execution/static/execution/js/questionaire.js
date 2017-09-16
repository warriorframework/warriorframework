var questionaire = {
  /*
  1. show just the first question
  2. if question # is 1 back button should be disabled.
  3. next should be enabled on specific exevents on every question.
  4. default next action wll be the next question.
  */
  form: '',
  qnList: '',
  dataList: '',
  currentQuestion: '',
  currentQuestionIndex: 0,
  qnPath: '',

  init: function(form){
      questionaire.form = form;
      questionaire.qnList = questionaire.form.find('.questionaire-qn');
      questionaire.dataList = questionaire.form.find('.questionaire-data');
      questionaire.qnPath = [];
      // questionaire.hideNav();
      questionaire.showQuestion(0);
  },

  showQuestion: function(index, onHittingPrevious){
    // get the list of questions
    var qnList = questionaire.qnList;
    questionaire.hideData();
    if(index===0){questionaire.qnPath = [];}


    for(i=0; i < qnList.length; i++) {
      if (i === index){
        $(qnList[i]).show();
        if(questionaire.currentQuestion){$(qnList[i]).attr('data-broughtBy', $(questionaire.currentQuestion).attr('name'));}
        questionaire.currentQuestion = qnList[i];
        questionaire.currentQuestionIndex = i;
        questionaire.qnPath.push(i);

      }else{
        $(qnList[i]).hide();
      }
    }
    questionaire.showNav(index);
    questionaire.showDataDisplayed();

  },

  hideData: function(){
    var dataList = questionaire.dataList;

    $.each(dataList, function(index, data){
      $(data).hide();
    });
  },

  showDataDisplayed: function(){
    var dataDisplayed = $(questionaire.currentQuestion).attr('data-displayed');
    if (dataDisplayed){
      var dataDisplayedList = dataDisplayed.split(',');
      questionaire.showItemFromList(dataDisplayedList);
    }
  },
  clearQnAttr: function(attrList){
    $.each(questionaire.qnList, function(index, qn){
      $.each(attrList, function(index, attr){
        $(qn).attr(attr, '');
      });
    });

  },

  hideNav: function(){
    // hide next, previous
    questionaire.form.find("[name=back]").hide();
    questionaire.form.find("[name=previous]").hide();
    questionaire.form.find("[name=next]").hide();
  },
  showNav: function(index){
    // hide next, previous
    var len = questionaire.qnList.length - 1;
    questionaire.hideNav();
    if (index === 0){
      questionaire.form.find("[name=next]").show();

    }
    else if(index === len) {
        questionaire.form.find("[name=previous]").show();
    }else {
        questionaire.form.find("[name=back]").show();
        questionaire.form.find("[name=previous]").show();
        questionaire.form.find("[name=next]").show();
      }
    },

  showItemFromList: function(showItemsList){
    $.each(showItemsList, function(index, value){
      item = questionaire.form.find('[name='+value+']');
      $(item).show();
    });
  },

  actOnInput: function(){
    // display only the requested data
    elem = $(this);
    questionaire.hideData();
    var showItems = elem.attr('data-show')
    if (showItems){
  		showItemsList = showItems.split(',');
  		// console.log(showItemsList);
  		questionaire.showItemFromList(showItemsList);
  	}
    // update the data-displayed
    $(questionaire.currentQuestion).attr('data-displayed', showItems)

    //set onNext value to the questionaire
    var setOnNext = elem.attr('data-setOnNext') ? elem.attr('data-setOnNext'): ""
    $(questionaire.currentQuestion).attr('data-onNext', setOnNext)

  },
  getNextValue: function(){
    var nextVal = questionaire.currentQuestionIndex + 1;
    var qnList = questionaire.qnList;
    var nextData = $(questionaire.currentQuestion).attr('data-onNext');
    if (nextData){
      $.each(qnList, function(index, qn){
        if ($(qn).attr('name') === nextData){
          nextVal = index;
        }
      });
    }
    return nextVal;
  },

  onNext: function(){
    var status = true;
    // call callbacks to perform validations beore going to nextVal
    var callBack = $(questionaire.currentQuestion).attr('data-nextValidation');
    if (callBack) {
      callBack = callBack + '(questionaire.form)';
      status = eval(callBack);
    }
    if(status){
      var nextVal = questionaire.getNextValue();
      questionaire.showQuestion(nextVal);
    }
  },
  getPreviousValue: function(){
    var previousVal = questionaire.currentQuestionIndex -1;
    var qnList = questionaire.qnList;
    var prevData = $(questionaire.currentQuestion).attr('data-broughtBy');
    if (prevData){
      $.each(qnList, function(index, qn){
        if ($(qn).attr('name') === prevData){previousVal = index;}
      });
      }
    return previousVal;
  },
  onPrevious: function(){
    var currIndex = questionaire.currentQuestionIndex;
    $.each(questionaire.qnPath, function(index, val){
      if(val == currIndex) {
        indReq = questionaire.qnPath[index - 1];
        return false;
      }
    });
    questionaire.showQuestion(indReq);
  },

  onBack: function(){
      var backVal = questionaire.currentQuestionIndex -1;
      questionaire.showQuestion(backVal, true);
  },
  startOver: function(){
    questionaire.resetFields();
    questionaire.init(questionaire.form);
  },
  resetFields: function(){
    /*
     use this to reset all the inputs in current questionaire
     by default resets the following
     - radio
     - text fields
     Also clears the following attributes of each question in the questionaire
     - data-displayed
    */
    radio_btns = questionaire.form.find("input[type='radio']");
    for(i=0; i < radio_btns.length; i++) {
      $(radio_btns[i]).prop('checked', false);
    }
    $(questionaire.form)[0].reset();
    questionaire.clearQnAttr(['data-displayed']);
  },

  submitQuestionaire: function(){
    callBack = $(this).attr('data-callBack')
    eval(callBack+'()');

  },




// ends
};
