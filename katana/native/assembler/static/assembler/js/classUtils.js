class kwRepository {
    constructor(data){
        this.url = data["@url"];
        this.label = data["@label"];
        this.clone = data["@clone"];
        this.all_drivers = data["@all_drivers"];
        this.drivers = [];
        console.log("12345");
        console.log(data["driver"]);
        for(var i=0; i<data["driver"].length; i++){
            console.log("Here");
            this.drivers.push(new driverDetails(data["driver"][i]));
        }
    }

    addDriver(name, clone){
        this.drivers.push(new driverDetails(name, clone))
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var $elem = $('<div>Sanika</div>');
        return $elem;
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
    constructor(data){
        console.log(data);
        this.name = data["@name"];
        this.clone = data["@clone"];
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
        var installed_btn = '<button class="btn btn-success" katana-click="assembler.installDependency" aria-selected="false">Install</button>';
        var available_txt = '<h6 class="card-subtitle mb-2 text-muted">&nbsp;</h6><br>';
        if(this.installed){
            available_txt = '<h6 class="card-subtitle mb-2 text-muted">Available Version: ' + this.installed + '</h6><br>';
            if(!this.matched){
                installed_btn = '<button class="btn btn-danger" katana-click="assembler.installDependency" aria-selected="false">Install</button>';
            }
            else if(this.matched == "lower"){
                installed_btn = '<button class="btn btn-info" katana-click="assembler.upgradeDependency" aria-selected="false">Upgrade&nbsp;<i class="fa fa-exclamation-triangle tan" aria-hidden="true"></i>&nbsp;</button>';
            }
            else if(this.matched == "higher"){
                installed_btn = '<button class="btn btn-success">Installed&nbsp;<i class="fa fa-check-circle green" aria-hidden="true"></i>&nbsp;</button>';
            }
            else{
                installed_btn = '<button class="btn btn-success">Installed&nbsp;<i class="fa fa-check-circle green" aria-hidden="true"></i>&nbsp;</button>';
            }
        }

        var html_contents = '<div style="padding: 1rem;">' +
                                '<div class="card" style="width: 350px; height:190px; padding: 1rem;">' +
                                    '<div class="card-block">' +
                                        '<h4 class="card-title">' + this.name +'</h4>' +
                                        '<h6 class="card-subtitle mb-2 text-muted">Version: ' + this.version + '</h6><hr>' +
                                        available_txt +
                                        installed_btn +
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