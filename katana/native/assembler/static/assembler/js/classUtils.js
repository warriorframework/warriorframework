class kwRepository {
    constructor(url, label, clone, all_drivers){
        this.url = url;
        this.label = label;
        this.clone = clone;
        this.all_drivers = all_drivers;
        this.drivers = []
    }

    addDriver(name, clone){
        this.drivers.push(new driverDetails(name, clone))
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var $elem = $('<div></div>');
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var driversJson = [];
        for(var i=0; i<this.drivers; i++){
            driversJson.push(drivers[i].jsonObj)
        }
        var jsonObject = {
            "@url": this.url,
            "@label": this.label,
            "@clone": this.clone,
            "@all_drivers": this.all_drivers,
            "driver": driversJson
        }
        return jsonObject;
    }

}

class driverDetails {
    constructor(name, clone){
        this.name = name;
        this.clone = clone;
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {
            "driver": {
                "@name": this.name,
                "@clone": this.clone
            }
        }
    }
}

class wsRepository {
    constructor(url, label, clone, overwrite){
        this.url = url;
        this.clone = clone;
        this.label = label;
        this.overwrite = overwrite;
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var html_contents = '<div></div>';
        var $elem = $(html_contents);
        return $elem
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {
            "@url": this.url,
            "@label": this.label,
            "@clone": this.clone,
            "@overwrite": this.overwrite,
        }
        return jsonObject;
    }
}

class dependency{
    constructor(data){
        this.name = data["@name"];
        this.install = data["@install"].toLowerCase().trim();
        this.user = data["@user"].toLowerCase().trim();
        this.version = data["version"];
        this.installed = data["installed"];
        this.matched = data["matched"];
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var install_cb = "";
        if(this.install == "yes"){
            install_cb = "checked";
        }
        var install_user = "";
        if(this.user == "yes"){
            install_user = "checked";
        }

        var installed_txt = '<p class="btn btn-danger">Not Available</p>';
        if(this.installed){
            installed_txt = '<p class="btn btn-success">Available Version: ' + this.installed + '</p>';
        }

        var matched_btn = '<button class="btn btn-success">Up To Date</button>';
        if(!this.installed){
            matched_btn = '<button class="btn btn-danger">Install</button>';
        }
        else if(this.matched == "lower"){
            matched_btn = '<button class="btn btn-danger">Needs Upgrade</button>';
        }

        var html_contents = '<div style="padding: 1rem;">' +
                                '<div class="card" style="width: 350px; height:150px; padding: 1rem;">' +
                                    '<div class="card-block">' +
                                        '<h4 class="card-title">' + this.name +'</h4>' +
                                        '<h6 class="card-subtitle mb-2 text-muted">Version: ' + this.version + '</h6><br>' +
                                        installed_txt + matched_btn +
                                    '</div>' +
                                '</div>' +
                            '</div>'
        var $elem = $(html_contents);
        return $elem
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {
            "@name": this.name,
            "@install": this.install,
            "@user": this.user,
        }
        return jsonObject;
    }
}

/*
let new_obj = new kwRepository("url", "label", "clone", "all_drivers")
console.log(new_obj)
new_obj.addDriver("driver_name", "clone_no")
new_obj.addDriver("driver_name_2", "clone_yes")
console.log(new_obj);
console.log(new_obj.jsonObj)
*/

let new_obj = new dependency({"@name": "jira", "@install": "YES", "@user": "NO"})
console.log(new_obj)