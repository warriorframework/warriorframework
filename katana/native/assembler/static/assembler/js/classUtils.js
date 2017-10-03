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
}

let new_obj = new kwRepository("url", "label", "clone", "all_drivers")

console.log(new_obj)

new_obj.addDriver("driver_name", "clone_no")
new_obj.addDriver("driver_name_2", "clone_yes")

console.log(new_obj);

console.log(new_obj.jsonObj)