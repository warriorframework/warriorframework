'use strict';

var leftTableContent = '<div class="cli-data-left-column-topbar">' +
                          '<div class="cli-data-left-column-topbar-header">' +
                              '<div class="">' +
                                  '<h6 id="display"></h6>' +
                              '</div>' +
                              '<div class="cli-data-left-column-topbar-header-top">' +
                                  '<h4 id="displayTitle"></h4>' +
                              '</div>' +
                          '</div>' +
                          '<div class="row cli-data-left-column-icons">' +
                              '<div class="col">' +
                                  '<i class="fa fa-plus"></i>' +
                              '</div>' +
                              '<div class="col">' +
                                  '<i class="fa fa-files-o"></i>' +
                              '</div>' +
                              '<div class="col">' +
                                  '<i class="fa fa-trash-o"></i>' +
                              '</div>' +
                              '<div class="col">' +
                                  '<i class="fa fa-chevron-left"></i>' +
                              '</div>' +
                              '<div class="col">' +
                                  '<i class="fa fa-chevron-right"></i>' +
                              '</div>' +
                          '</div>' +
                      '</div>' +
                      '<div id="left-content" class="cli-data-left-content"></div>';

var leftColumnInputs = '<div class="row">' +
                           '<div class="col-sm-4 cli-data-left-content-label"></div>' +
                           '<div class="col-sm-8 cli-data-left-content-value">' +
                               '<input class="cli-data-left-content-value-input">' +
                           '</div>' +
                       '</div>';

var leftColumnSelects = '<div class="row">' +
                            '<div class="col-sm-4 cli-data-left-content-label"></div>' +
                            '<div class="col-sm-8 cli-data-left-content-value">' +
                                '<select class="cli-data-left-content-value-input"></select>' +
                            '</div>' +
                        '</div>';

var rightColumnTable = '<div class="cli-data-right-column-topbar">' +
                           '<div class="cli-data-right-column-topbar-header">' +
                               '<div class="cli-data-right-column-topbar-header-top">' +
                                   '<h6 id="section"></h6>' +
                               '</div>' +
                               '<div class="cli-data-right-column-topbar-header-bottom">' +
                                   '<h4 id="sectionTitle"></h4>' +
                               '</div>' +
                           '</div>' +
                           '<div class="row cli-data-right-column-icons">' +
                               '<div class="col">' +
                                   '<i class="fa fa-thumb-tack" aria-hidden="true"></i>' +
                               '</div>' +
                           '</div>' +
                       '</div>' +
                       '<div class="cli-data-right-content" style="display: none;">' +
                           '<ul></ul>' +
                       '</div>' +
                       '<br>';

var rightColumnTableInputs = '<li>' +
                                 '<div class="cli-data-labels">' +
                                     '<div></div>' +
                                 '</div>' +
                                 '<div class="cli-data-columns">' +
                                     '<div></div>' +
                                 '</div>' +
                            '</li>';

/* Parent Command Class */

class command{
    constructor(data){
        if(data === undefined){
            data = {};
        }
        this.sys = !data["@sys"] ? this.getDefaults("sys") : data["@sys"];
        this.session = !data["@session"] ? this.getDefaults("session") : data["@session"];
        this.start = !data["@start"] ? this.getDefaults("start") : data["@start"];
        this.end = !data["@end"] ? this.getDefaults("end") : data["@end"];
        this.timeout = !data["@timeout"] ? this.getDefaults("timeout") : data["@timeout"];
        this.sleep = !data["@sleep"] ? this.getDefaults("sleep") : data["@sleep"];
        this.verify = !data["@verify"] ? this.getDefaults("verify") : data["@verify"];
        this.retry = this.converter("retry", data["@retry"], false, true);
        this.retry_timer = !data["@retry_timer"] ? this.getDefaults("retry_timer") : data["@retry_timer"];
        this.retry_count = !data["@retry_count"] ? this.getDefaults("retry_count") : data["@retry_count"];
        this.retry_onmatch = !data["@retry_onmatch"] ? this.getDefaults("retry_onmatch") : data["@retry_onmatch"];
        this.resp_req = this.converter("resp_req", data["@resp_req"], false, true);
        this.resp_pat_req = !data["@resp_pat_req"] ? this.getDefaults("resp_pat_req") : data["@resp_pat_req"];
        this.resp_ref = !data["@resp_ref"] ? this.getDefaults("resp_ref") : data["@resp_ref"];
        this.resp_keys = !data["@resp_keys"] ? this.getDefaults("resp_keys") : data["@resp_keys"];
        this.inorder_resp_ref = this.converter("inorder_resp_ref", data["@inorder_resp_ref"], false, true);
        this.inorder = this.converter("inorder", data["@inorder"], false, true);
        this.monitor = !data["@monitor"] ? this.getDefaults("monitor") : data["@monitor"];
        this.repeat = this.converter("repeat", data["@repeat"], false, true);
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){

            var jsonObject = {
                "@sys": (this.sys === "") ? this.getDefaults("sys") : this.sys,
                "@session": (this.session === "") ? this.getDefaults("session") : this.session,
                "@start": (this.start === "") ? this.getDefaults("start") : this.start,
                "@end": (this.end === "") ? this.getDefaults("end") : this.end,
                "@timeout": (this.timeout === "") ? this.getDefaults("timeout") : this.timeout,
                "@sleep":(this.sleep === "") ? this.getDefaults("sleep") : this.sleep,
                "@verify": (this.verify === "") ? this.getDefaults("verify") : this.verify,
                "@retry": this.converter("retry", this.retry, true, false),
                "@retry_timer": (this.retry_timer === "") ? this.getDefaults("retry_timer") : this.retry_timer,
                "@retry_count": (this.retry_count === "") ? this.getDefaults("retry_count") : this.retry_count,
                "@retry_onmatch": (this.retry_onmatch === "") ? this.getDefaults("retry_onmatch") : this.retry_onmatch,
                "@resp_req": this.converter("resp_req", this.resp_req, true, false),
                "@resp_pat_req": (this.resp_pat_req === "") ? this.getDefaults("resp_pat_req") : this.resp_pat_req,
                "@resp_ref": (this.resp_ref === "") ? this.getDefaults("resp_ref") : this.resp_ref,
                "@resp_keys": (this.resp_keys === "") ? this.getDefaults("resp_keys") : this.resp_keys,
                "@inorder_resp_ref": this.converter("inorder_resp_ref", this.inorder_resp_ref, true, false),
                "@inorder": this.converter("inorder", this.inorder, true, false),
                "@monitor": (this.monitor === "") ? this.getDefaults("monitor") : this.monitor,
                "@repeat": this.converter("repeat", this.repeat, true, false)
            }
            return jsonObject;
    }

    getDefaults(key){
        var defaults = {
            "sys": "",
            "session": "",
            "start": ".*",
            "end": "",
            "timeout": "60" ,
            "sleep": "0",
            "verify": "",
            "retry": "n",
            "retry_timer": "60",
            "retry_count": "5",
            "retry_onmatch": "",
            "resp_req": "",
            "resp_pat_req": "",
            "resp_ref": "",
            "resp_keys": "",
            "inorder_resp_ref": "",
            "monitor": "",
            "inorder": "",
            "repeat": ""
        }
        return defaults[key]
    }

    converter(key, value, toJson, toEnglish){
        var posPattern = new RegExp('^yes|y$','gi');
        var negPattern = new RegExp('^no|n$','gi');
        var direction = false;

        if(!toEnglish){
            direction = "toJson";
        } else {
            direction = "toEnglish";
        }

        var keys = {
            "retry": {
                "toJson": (value == "Yes") ? "y" : this.getDefaults("retry"),
                "toEnglish": (value !== undefined && value.toLowerCase().trim().match(posPattern)) ? "Yes" : "No"
            },
            "resp_req": {
                "toJson": (value == "Yes") ? "y" : this.getDefaults("resp_req"),
                "toEnglish": (value !== undefined && value.toLowerCase().trim().match(negPattern)) ? "No" : "Yes"
            },
            "inorder": {
                "toJson": (value == "Yes") ? "y" : this.getDefaults("inorder"),
                "toEnglish": (value !== undefined && value.toLowerCase().trim().match(posPattern)) ? "Yes" : "No"
            },
            "repeat": {
                "toJson": (value == "Yes") ? "y" : this.getDefaults("repeat"),
                "toEnglish": (value !== undefined && value.toLowerCase().trim().match(posPattern)) ? "Yes" : "No"
            },
            "inorder_resp_ref":{
                "toJson": (value == "No") ? "n" : this.getDefaults("inorder_resp_ref"),
                "toEnglish": (value !== undefined && value.toLowerCase().trim().match(negPattern)) ? "No" : "Yes"
            }
        };
        return keys[key][direction]
    }
}

/* Global Command Class */

class globalCommand extends command{

    constructor(data){
        super();
        this.orderedVariables = this.getOrderedVariables();
    }

    getOrderedVariables() {
        var orderedVariables = [
            {"System": {"value": this.sys, "type": "input"}},
            {"Session": {"value": this.session, "type": "input"}},
            {"Start": {"value": this.start, "type": "input"}},
            {"End": {"value": this.end, "type": "input"}},
            {"Timeout": {"value": this.timeout, "type": "input"}},
            {"Sleep": {"value": this.sleep, "type": "input"}},
            {"Verify": {"value": this.verify, "type": "input"}},
            {"Retry": {"value": this.retry, "type": "dropdown", "options": ["Yes", "No"]}},
            {"Retry Timer": {"value": this.retry_timer, "type": "input"}},
            {"Retry Count": {"value": this.retry_count, "type": "input"}},
            {"Retry On Match": {"value": this.retry_onmatch, "type": "input"}},
            {"Response Required": {"value": this.resp_req, "type": "dropdown", "options": ["Yes", "No"]}},
            {"Response Pattern Required": {"value": this.resp_pat_req, "type": "input"}},
            {"Response Reference": {"value": this.resp_ref, "type": "input"}},
            {"Response Keys": {"value": this.resp_keys, "type": "input"}},
            {"In-order Response Reference": {"value": this.inorder_resp_ref, "type": "dropdown", "options": ["Yes", "No"]}},
            {"Monitor": {"value": this.monitor, "type": "input"}},
            {"In-order": {"value": this.inorder, "type": "dropdown", "options": ["Yes", "No"]}},
            {"Repeat": {"value": this.repeat, "type": "dropdown", "options": ["Yes", "No"]}}
        ];
        return orderedVariables
    }

    get htmlLeftContent() {
        return this.formHtmlLeftContent();
    }

    formHtmlLeftContent(){
        var $content = $(leftTableContent);
        $content.find('#display').text("Global");
        $content.find('#displayTitle').text("Command Parameters");
        var $subContent = false;
        for(var i=0; i<this.orderedVariables.length; i++){
            for(var key in this.orderedVariables[i]){
                if(this.orderedVariables[i][key]["type"] == "input"){
                    $subContent = $(leftColumnInputs);
                    $subContent.find('.cli-data-left-content-label').text(key);
                    $subContent.find('.cli-data-left-content-value-input').val(this.orderedVariables[i][key]["value"]);
                } else {
                    $subContent = $(leftColumnSelects);
                    $subContent.find('.cli-data-left-content-label').text(key);
                    console.log(this.orderedVariables[i][key]["options"]);
                    for(var j=0; j<this.orderedVariables[i][key]["options"].length; j++){
                        console.log(this.orderedVariables[i][key]["options"][j]);
                        $subContent.find('.cli-data-left-content-value-input').append($('<option>' + this.orderedVariables[i][key]["options"][j]  + '</option>'))
                    }
                    $subContent.find('.cli-data-left-content-value-input').val(this.orderedVariables[i][key]["value"]);
                }
                $($content[1]).append($subContent);
                break;
            }
        }
        return $content;
    }

}

/* Testdata Command Class */

class testdataCommand extends command{
    constructor(data){
        super(data);
        this.send = !data["@send"] ? this.getDefaults("send") : data["@send"];
    }

    getDefaults(key){
        var defaults = {
            "send": ""
        }
        if(key in defaults){
            return defaults[key];
        } else {
            return super.getDefaults(key);
        }
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = super.formJsonObj();
        jsonObject["@send"] = (this.send === "") ? this.getDefaults("send") : this.send;
        return jsonObject;
    }
}

/* Testdata Class */

class testdata{

    constructor(data){
        if(data === undefined){
            data = {};
        }
        this.title = !data["@title"] ? this.getDefaults("title") : data["@title"];
        this.row = !data["@row"] ? this.getDefaults("row") : data["@row"];
        this.monitor = !data["@monitor"] ? this.getDefaults("monitor") : data["@monitor"];
        this.execute = this.converter("execute", data["@execute"], false, true);
        this.iter_type = this.converter("iter_type", data["@iter_type"], false, true);
    }

    converter(key, value, toJson, toEnglish){
        var posPattern = new RegExp('^yes|y$','gi');
        var negPattern = new RegExp('^no|n$','gi');
        var direction = false;

        var keys = {
            "iter_type": {
                "toJson" : (value == "Per Command") ? "per_cmd" : this.getDefaults(key),
                "toEnglish": (value !== undefined && value.toLowerCase().trim() == "per_cmd") ? "Per Command" : "Per CLI-Data Block"
            },
            "execute": {
                "toJson": (value == "No") ? "no" : this.getDefaults("execute"),
                "toEnglish": (value !== undefined && value.toLowerCase().trim().match(negPattern)) ? "No" : "Yes"
            }
        }

        var direction = "toJson";
        if(toEnglish){
            direction = "toEnglish";
        }

        return keys[key][direction]
    }

    getDefaults(key){
        var defaults = {
            "title": "",
            "row": "",
            "monitor": "",
            "execute": "yes",
            "iter_type": "per_td_block"
        }

        return defaults[key];
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {
            "@title": (this.title === "") ? this.getDefaults("title") : this.title,
            "@row": (this.row === "") ? this.getDefaults("row") : this.row,
            "@monitor": (this.monitor === "") ? this.getDefaults("monitor") : this.monitor,
            "@execute": this.converter("execute", this.execute, true, false),
            "@iter_type": this.converter("iter_type", this.iter_type, true, false)
        };
        return jsonObject;
    }
}

/* Verifications Class */

class verifications{
    constructor(data){
        this.cond_type_toJson = {"String": "str", "Integer": "int", "Float": "float"};
        this.cond_type_toEnglish = this.flipObject(this.cond_type_toJson);
        this.cond_type_options = this.getOptionsFromMappings(this.cond_type_toJson)
        this.operator_toJson = {"Equal To": "eq", "Not Equal To": "ne", "Greater Than": "gt",
                                 "Greater Than Or Equal To": "ge", "Lesser Than": "lt",
                                 "Lesser Than Or Equal To": "le"};
        this.operator_toEnglish = this.flipObject(this.operator_toJson);
        this.operator_options = this.getOptionsFromMappings(this.operator_toJson);

        if(data === undefined || data === {}){
            data = {"verification": {}}
        }
        for(var key in data){
            if(data.hasOwnProperty(key)){
                this.name = key;
                this.type = "verification";
                this.found = this.converter("found", data[this.name]["@found"], false, true);
                this.search = !data[this.name]["@search"] ? this.getDefaults("search") : data[this.name]["@search"];
                this.verify_on = !data[this.name]["@verify_on"] ? this.getDefaults("verify_on") : data[this.name]["@verify_on"];
                this.cond_value = !data[this.name]["@cond_value"] ? this.getDefaults("cond_value") : data[this.name]["@cond_value"];
                this.cond_type = this.converter("cond_type", data[this.name]["@cond_type"], false, true);
                this.operator = this.converter("operator", data[this.name]["@operator"], false, true);
                break;
            }
        }
    }

    converter(key, value, toJson, toEnglish){
        var posPattern = new RegExp('^yes|y$','gi');
        var negPattern = new RegExp('^no|n$','gi');
        var direction = false;

        var keys = {
            "found": {
                "toJson" : (value == "No") ? "no" : this.getDefaults(key),
                "toEnglish": (value !== undefined && value.toLowerCase().trim() == "no") ? "No" : "Yes"
            },
            "cond_type": {
                "toJson" : (value !== undefined) ? this.cond_type_toJson[value]: this.cond_type_toJson[this.getDefaults(key)],
                "toEnglish": (value !== undefined) ? this.cond_type_toEnglish[value.toLowerCase().trim()] : this.cond_type_toEnglish[this.getDefaults(key)]
            },
            "operator": {
                "toJson" : (value !== undefined) ? this.operator_toJson[value]: this.operator_toJson[this.getDefaults(key)],
                "toEnglish": (value !== undefined) ? this.operator_toEnglish[value.toLowerCase().trim()] : this.operator_toEnglish[this.getDefaults(key)]
            }
        }

        var direction = "toJson";
        if(toEnglish){
            direction = "toEnglish";
        }

        return keys[key][direction]
    }

    getDefaults(key){
        var defaults = {
            "search": "",
            "verify_on": "",
            "found": "yes",
            "cond_value": "",
            "cond_type": "str",
            "operator": "eq"
        }

        return defaults[key];
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {};
        jsonObject[this.name] = {
            "@search": (this.search === "") ? this.getDefaults("search") : this.search,
            "@verify_on": (this.verify_on === "") ? this.getDefaults("verify_on") : this.verify_on,
            "@found": this.converter("found", this.found, true, false),
            "@cond_value": (this.cond_value === "") ? this.getDefaults("cond_value") : this.cond_value,
            "@cond_type": this.converter("cond_type", this.cond_type, true, false),
            "@operator": this.converter("operator", this.operator, true, false)
        };
        return jsonObject;
    }

    getOptionsFromMappings(mappings){
        var new_set = new Set([]);
        for(var key in mappings){
            if(mappings.hasOwnProperty(key)){
                new_set.add(key)
            }
        }
        return new_set;
    }

    flipObject(mappings){
        var flipped_mappings = {};
        for(var key in mappings){
            if(mappings.hasOwnProperty(key)){
                flipped_mappings[mappings[key]] = key;
            }
        }
        return flipped_mappings;
    }
}

/* Global Verifications Class */

class globalVerifications extends verifications{

}

/* Testdata Verifications Class */

class testdataVerifications extends verifications{

}

/* Combinations Class */

class combinations{
    constructor(data){
        if(data === undefined || data === {}){
            data = {"combination": {}}
        }
        for(var key in data){
            if(data.hasOwnProperty(key)){
                this.name = key;
                this.type = "combination";
                this.combo = !data[this.name]["@combo"] ? this.getDefaults("combo") : data[this.name]["@combo"];
                break;
            }
        }
    }

    getDefaults(key){
        var defaults = {
            "combo": ""
        }
        return defaults[key];
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {};
        jsonObject[this.name] = {
            "@combo": (this.combo === "") ? this.getDefaults("combo") : this.combo,
        };
        return jsonObject;
    }
}

/* Global Combinations Class */

class globalCombinations extends combinations{

}

/* Testdata Combinations Class */

class testdataCombinations extends combinations{

}

/* Global Keys Class */

class keys{
    constructor(data){
        if(data === undefined || data === {}){
            data = {"key": {}}
        }
        for(var key in data){
            if(data.hasOwnProperty(key)){
                this.name = key;
                this.type = "key";
                this.resp_pattern_req = !data[this.name]["@resp_pattern_req"] ? this.getDefaults("resp_pattern_req") : data[this.name]["@resp_pattern_req"];
                break;
            }
        }
    }

    getDefaults(key){
        var defaults = {
            "resp_pattern_req": ""
        }
        return defaults[key];
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {};
        jsonObject[this.name] = {
            "@resp_pattern_req": (this.resp_pattern_req === "") ? this.getDefaults("resp_pattern_req") : this.resp_pattern_req,
        };
        return jsonObject;
    }
}

/* Global Keys Class */

class globalKeys extends keys{

}

/* Testdata Combinations Class */

class testdataKeys extends keys{

}