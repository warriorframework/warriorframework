'use strict';

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
        this.inorder = this.converter("inorder", data["@inorder"], false, true);
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
                "@inorder": this.converter("inorder", this.inorder, true, false),
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
            "retry_timer": "60",
            "retry_count": "5",
            "retry_onmatch": "",
            "inorder": "",
            "repeat": "",
            "retry": "n",
            "resp_req": "",
            "resp_pat_req": "",
            "resp_ref": ""
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
            }
        };
        return keys[key][direction]
    }
}

class globalCommand extends command{

    constructor(data){
        super(data);
        this.iter_type = this.converter("iter_type", data["@iter_type"], false, true);
    }

    converter(key, value, toJson, toEnglish){
        var keys = {
            "iter_type": {
                "toJson" : (value == "Per Command") ? "per_cmd" : this.getDefaults(key),
                "toEnglish": (value !== undefined && value.toLowerCase().trim() == "per_cmd") ? "Per Command" : "Per CLI-Data Block"
            }
        }

        if(!(keys.hasOwnProperty(key))){
            return super.converter(key, value, toJson, toEnglish);
        } else {
            var direction = "toJson";
            if(toEnglish){
                direction = "toEnglish";
            }

            return keys[key][direction]
        }
    }

    getDefaults(key){
        var defaults = {
            "iter_type": "per_td_block"
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
        jsonObject["@iter_type"] = this.converter("iter_type", this.iter_type, true, false);
        return jsonObject;
    }
}

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

let cmd_obj = new testdataCommand({"@sleep": "55", "@send": "command"});
console.log(cmd_obj);
cmd_obj.retry_count = "10";
console.log(cmd_obj.retry_count)
console.log(cmd_obj.jsonObj);
