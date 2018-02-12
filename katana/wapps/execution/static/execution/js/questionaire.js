var questionaire = {
  /*
  questionaire object
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
      // questionaire.showQuestion(0);
  },

  showQuestion: function(index, onHittingPrevious){
    /*
    called by other questionaire objects.
    show the question to be dataDisplayed
    */
    var qnObject = $(this)[0];
    var qnList = qnObject.qnList;
    qnObject.hideData();
    if(index===0){qnObject.qnPath = [];}


    for(i=0; i < qnList.length; i++) {
      if (i === index){
        $(qnList[i]).show();
        if(qnObject.currentQuestion){$(qnList[i]).attr('data-broughtBy', $(qnObject.currentQuestion).attr('name'));}
        qnObject.currentQuestion = qnList[i];
        qnObject.currentQuestionIndex = i;
        qnObject.qnPath.push(i);

      }else{
        $(qnList[i]).hide();
      }
    }
    qnObject.setNav(index);
    qnObject.showDataDisplayed();

  },

  hideData: function(){
    /*
    called by other questionaire objects.
    hides all the data related to the questionaire
    */
    var qnObject = $(this)[0];
    var dataList = qnObject.dataList;
    $.each(dataList, function(index, data){
      $(data).hide();
    });
  },

  showDataDisplayed: function(){
    /*
    called by other questionaire objects.
    shows the data sections as available in the data-displayed attribute of the current question
    */
    var qnObject = $(this)[0];
    var dataDisplayed = $(qnObject.currentQuestion).attr('data-displayed');
    if (dataDisplayed){
      var dataDisplayedList = dataDisplayed.split(',');
      qnObject.showItemFromList(dataDisplayedList);
    }
  },
  clearQnAttr: function(attrList){
    /*
    called by other questionaire objects.
    iterattes over each question in the questionaire and clears the attributes specified in the attrList.
    */
    var qnObject = $(this)[0];
    $.each(qnObject.qnList, function(index, qn){
      $.each(attrList, function(index, attr){
        $(qn).attr(attr, '');
      });
    });
  },
  disableNav: function(disableList){
    /*
    disable the navigation elements specified in the disableList
    */
    $.each(disableList, function(index, item){
      item.prop('disabled', true);
      item.addClass('disabled');
    });
  },
  enableNav: function(enableList){
    /*
    enables the navigation elements specified in the disableList
    */
    $.each(enableList, function(index, item){
      item.prop('disabled', false);
      item.removeClass('disabled');
    });
  },
  setNav: function(index){
    /*
    called by other questionaire objects.
    set the navigation enable or disable based on the form index
    */
    var qnObject = $(this)[0];
    var len = qnObject.qnList.length - 1;
    var prev = qnObject.form.find("[name=previous]");
    var next = qnObject.form.find("[name=next]");
    var submit = qnObject.form.find("[name=submit]");

    // initially disable next, previous
    qnObject.disableNav([prev, next, submit]);


    if (len === 0){
      // if only one qestion in the questionaire enable submit
        questionaire.enableNav([submit]);
    }
    else if (len > 0 & index === 0){
      // if 1st question enable next,
      questionaire.enableNav([next]);
    }
    else if(len >0 & index === len) {
        // if last question enable previous, submit
        questionaire.enableNav([prev, submit]);
    }else {
        // if not first, not last enable both next, previous
        questionaire.enableNav([next, prev]);
      }
    },

  showItemFromList: function(showItemsList){
    // called from other qnobject methods
    var qnObject = $(this)[0];

    $.each(showItemsList, function(index, value){
      item = qnObject.form.find('[name='+value+']');
      $(item).show();
    });
  },

  actOnInput: function(){
    // will be called by UI interaction
    // display only the requested data
    var elem = $(this);
    qnObject = questionaire.getQnObject(elem);
    qnObject.hideData();
    var showItems = elem.attr('data-show')
    if (showItems){
  		showItemsList = showItems.split(',');
  		// console.log(showItemsList);
  		qnObject.showItemFromList(showItemsList);
  	}
    // update the data-displayed
    $(qnObject.currentQuestion).attr('data-displayed', showItems)

    //set onNext value to the questionaire
    var setOnNext = elem.attr('data-setOnNext') ? elem.attr('data-setOnNext'): ""
    $(qnObject.currentQuestion).attr('data-onNext', setOnNext)

  },
  getQnObject: function(elem){
    // gets the questionaire object associated to the form
    var closestForm = elem.closest('form');
    var qnObject = closestForm.data('questionaireObject');
    return qnObject;
  },
  onPrevious: function(){
    // called on clicking previous button
    var elem = $(this);
    qnObject = questionaire.getQnObject(elem);
    var currIndex = qnObject.currentQuestionIndex;
    $.each(qnObject.qnPath, function(index, val){
      if(val == currIndex) {
        indReq = qnObject.qnPath[index - 1];
        return false;
      }
    });
    qnObject.showQuestion(indReq);
  },
  onNext: function(){
    // called on clicking next button
    var status = true;
    var elem = $(this);
    qnObject = questionaire.getQnObject(elem);
    // call callbacks to perform validations beore going to nextVal
    var callBack = $(qnObject.currentQuestion).attr('data-nextValidation');
    if (callBack) {
      callBack = callBack + '(qnObject.form)';
      status = eval(callBack);
    }
    if(status){
      var nextVal = qnObject.getNextValue();
      qnObject.showQuestion(nextVal);
    }
  },
  getNextValue: function(){
    // called from other qnobject methods
    var qnObject = $(this)[0];
    var nextVal = qnObject.currentQuestionIndex + 1;
    var qnList = qnObject.qnList;
    var nextData = $(qnObject.currentQuestion).attr('data-onNext');
    if (nextData){
      $.each(qnList, function(index, qn){
        if ($(qn).attr('name') === nextData){
          nextVal = index;
        }
      });
    }
    return nextVal;
  },
  getPreviousValue: function(){
    // called from other qnobject methods
    var qnObject = $(this)[0];
    var previousVal = qnObject.currentQuestionIndex -1;
    var qnList = qnObject.qnList;
    var prevData = $(qnObject.currentQuestion).attr('data-broughtBy');
    if (prevData){
      $.each(qnList, function(index, qn){
        if ($(qn).attr('name') === prevData){previousVal = index;}
      });
      }
    return previousVal;
  },
  startOver: function(callBack){
    // called by reset button
    var elem = $(this);
    qnObject = questionaire.getQnObject(elem);
    callBack = $(this).attr('data-callBack');
    if(callBack){
      callBack = callBack + '(qnObject.form)';
      eval(callBack);
    }
    qnObject.resetFields();
    qnObject.init(qnObject.form);
  },
  resetFields: function(){
    /*
     called from other qnobject methods
     use this to reset all the inputs in current questionaire
     by default resets the following
     - radio
     - text fields
     Also clears the following attributes of each question in the questionaire
     - data-displayed
    */
    var qnObject = $(this)[0];
    radio_btns = qnObject.form.find("input[type='radio']");
    for(i=0; i < radio_btns.length; i++) {
      $(radio_btns[i]).prop('checked', false);
    }
    $(qnObject.form)[0].reset();
    qnObject.clearQnAttr(['data-displayed']);
  },

  submitQuestionaire: function(){
    // called by clicking submit button
    var elem = $(this);
    qnObject = questionaire.getQnObject(elem);
    callBack = $(this).attr('data-callBack');
    status = eval(callBack+'()');
    // if(status){
    //   qnObject.form.hide();
    // }


  },
  closeQuestionaire: function(){
    var elem = $(this);
    qnObject = questionaire.getQnObject(elem);
    qnObject.form.hide();
  },

// ends
};
