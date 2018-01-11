class kwRepository {
    constructor(data){
        if(!data || data === undefined){
            data = {};
        }
        if(data["name"]){
            this.name = data["name"];
        } else {
            this.name = "Enter Repository Details"
        }
        if(data["@url"]){
            this.url = data["@url"];
        } else {
            this.url = ""
        }
        if(data["@label"]){
            this.label = data["@label"];
        } else {
            this.label = ""
        }
        if(data["@clone"]){
            this.clone = data["@clone"].toLowerCase().trim();
        } else {
            this.clone = "yes"
        }
        if(data["@all_drivers"]){
            this.all_drivers = data["@all_drivers"].toLowerCase().trim();
        } else {
            this.all_drivers = "yes";
        }
        if(data["available"]){
            this.available = data["available"];
        } else {
            this.available = true;
        }
        this.drivers = [];
        if(data["driver"]){
            for(var i=0; i<data["driver"].length; i++){
                this.drivers.push(new driverDetails({"@name": data["driver"][i]["@name"], "@clone": data["driver"][i]["@clone"]}));
            }
        }
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var clone_icon = "fa fa-toggle-off grey";
        if(this.clone === "yes"){
            clone_icon = "fa fa-toggle-on skyblue";
        }
        var available_icon = "fa fa-times red";
        var available_text = "Repository Not Available";
        if(this.available){
            available_icon = "fa fa-check-circle skyblue";
            available_text = "Repository Available"
        }
        var hideAvailability = "";
        if(this.url === ""){
            hideAvailability = "display: none";
        }
        var driverDom = '';
        for(var i=0; i<this.drivers.length; i++){
            driverDom = driverDom + this.drivers[i].domElement;
        }
        var displayDrivers = "";
        if(this.url === ""){
            displayDrivers = "display: none";
        }
        var allDriversIcon = "fa fa-toggle-off grey";
        var aria_selected_all_drivers = "false";
        if(this.all_drivers === "yes"){
            allDriversIcon = "fa fa-toggle-on skyblue";
            aria_selected_all_drivers = "true";
        }
        var $elem =  $('<div class="card border-secondary" style="padding: 1rem;">' +
                            '<div class="card-header assembler-no-bg">' +
                                '<div class="row">' +
                                    '<div class="col-sm-1">' +
                                        '<i class="' + clone_icon + ' assembler-icon-pos-right" key="kwRepoClone" ' +
                                            'aria-hidden="true" katana-click="assembler.toggleKwRepoClone" aria-selected="true"></i>' +
                                    '</div>' +
                                    '<div class="col-sm-7">' +
                                        this.name +
                                    '</div>' +
                                    '<div class="col-sm-2">' +
                                        '<i class="fa fa-trash" style="float:right;" ' +
                                            'aria-hidden="true" katana-click="assembler.deleteKwRepo" aria-selected="true" key="kwRepodelete"></i>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<div class="card-block" style="padding: 1rem;">' +
                                '<div class="row">' +
                                    '<div class="col-sm-1" style="text-align: right; padding: 0.7rem;">' +
                                        '<label>URL:</label>' +
                                    '</div>' +
                                    '<div class="col-sm-5">' +
                                        '<input key="kwRepo" value="' + this.url + '" katana-change="assembler.updateKwRepoDetails">' +
                                    '</div>' +
                                    '<div class="col-sm-1" style="text-align: right; padding: 0.7rem;">' +
                                        '<label>Label:</label>' +
                                    '</div>' +
                                    '<div class="col-sm-3">' +
                                        '<input key="kwRepoLabel" value="' + this.label + '">' +
                                    '</div>' +
                                '</div>' +
                                '<div class="row" style="' + displayDrivers + '">' +
                                    '<div class="col-sm-1"></div>' +
                                    '<div class="col-sm-9">' +
                                        '<div class="card">' +
                                            '<div class="card-header assembler-no-bg">' +
                                                '<i class="' + allDriversIcon + '" katana-click="assembler.toggleAllDrivers" ' +
                                                    ' key="kwRepoAllDrivers" aria-selected="' + aria_selected_all_drivers + '"></i>&nbsp;' +
                                                '<label>All Available Drivers</label>' +
                                            '</div>' +
                                            '<div class="card-block" style="padding: 1rem;">' +
                                                '<div class="row">' +
                                                    driverDom +
                                                '</div>' +
                                            '</div>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>'+
                                '<br>' +
                            '</div>' +
                            '<div class="card-footer assembler-no-bg">' +
                                '<div class="row" style="' + hideAvailability + '">' +
                                    '<div class="col-sm-1">' +
                                        '<i class="' + available_icon + ' assembler-icon-pos-right"></i>' +
                                    '</div>' +
                                    '<div class="col-sm-8 text-muted">' +
                                        available_text +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                        '<br>');
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
        };
        return jsonObject;
    }

}

class driverDetails {
    constructor(data){
        this.name = data["@name"];
        this.clone = data["@clone"];
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        if(this.name){
            var clone_icon = "fa fa-toggle-off grey";
            var aria_attribute = "false";
            if(this.clone === "yes"){
                clone_icon = "fa fa-toggle-on skyblue";
                aria_attribute = "true";
            }
            var elem = '<div class="col-sm-4">' +
                            '<i class="' + clone_icon + '" style="float: left; line-height: inherit !important" ' +
                            ' key="kwRepoDriver" katana-click="assembler.toggleDriverClone" aria-selected="' + aria_attribute + '"></i>&nbsp;' +
                            '<label style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; width: 270px;">' + this.name + '</label>' +
                        '</div>';
        }
        else{
            var elem = "";
        }

        return elem;
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {
            "@name": this.name,
            "@clone": this.clone
        };
        return jsonObject;
    }

}

class wsRepository {
    constructor(data){
        if(!data || data === undefined){
            data = {};
        }
        if(data["name"]){
            this.name = data["name"];
        } else {
            this.name = "Enter Repository Details"
        }
        if(data["@url"]){
            this.url = data["@url"];
        } else {
            this.url = "";
        }
        if(data["@clone"]){
            this.clone = data["@clone"].toLowerCase().trim();
        } else {
            this.clone = "yes";
        }
        if(data["@label"]){
            this.label = data["@label"];
        } else {
            this.label = "";
        }
        if(data["@overwrite"]){
            this.overwrite = data["@overwrite"].toLowerCase().trim();
        } else {
            this.overwrite = "yes";
        }
        this.available = data["available"];
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var cloneWsRepoIcon = "fa fa-toggle-off grey";
        var wsCloneToggle = "false";
        if(this.clone === "yes"){
            cloneWsRepoIcon = "fa fa-toggle-on skyblue";
            wsCloneToggle = "true";
        }

        var overwriteWsFiles = "fa fa-toggle-off grey";
        var overwriteSelect = "false";
        if(this.overwrite === "yes"){
            overwriteWsFiles = "fa fa-toggle-on skyblue";
            overwriteSelect = "true";
        }
        var hideAvailability = "";
        if(this.url === ""){
            hideAvailability = "display: none";
        }
        var wsAvailableIcon = "fa fa-times red";
        var wsAvailabvarext = "Repository Not Available";
        if(this.available){
            wsAvailableIcon = "fa fa-check-circle skyblue";
            wsAvailabvarext = "Repository Available"
        }
        var html_contents = '<div class="card border-secondary" style="padding: 1rem;">' +
                                '<div class="card-header assembler-no-bg">' +
                                    '<div class="row">' +
                                        '<div class="col-sm-1">' +
                                            '<i class="' + cloneWsRepoIcon + ' assembler-icon-pos-right" ' +
                                            'aria-selected="' + wsCloneToggle + '" katana-click="assembler.toggleWsRepoClone" aria-hidden="true" ' +
                                            'key="wsRepoClone"></i>' +
                                        '</div>' +
                                        '<div class="col-sm-5">' +
                                            this.name +
                                        '</div>' +
                                        '<div class="col-sm-1">' +
                                            '<i class="' + overwriteWsFiles + ' assembler-icon-pos-right" key="wsRepoOverwrite" ' +
                                                'katana-click="assembler.toggleWsOverwriteButton"  aria-hidden="true" aria-selected="' + overwriteSelect + '"></i>' +
                                        '</div>' +
                                        '<div class="col-sm-1">' +
                                            'Overwrite' +
                                        '</div>' +
                                        '<div class="col-sm-2">' +
                                            '<i class="fa fa-trash" katana-click="assembler.deleteWsRepo" key="wsRepodelete"' +
                                                    'aria-hidden="true" style="float: right;"></i>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="card-block" style="padding: 1rem;">' +
                                    '<div class="row">' +
                                        '<div class="col-sm-1" style="text-align: right; padding: 0.7rem;">' +
                                            '<label>URL:</label>' +
                                        '</div>' +
                                        '<div class="col-sm-5">' +
                                            '<input key="wsRepo" value="' + this.url + '" katana-change="assembler.checkWsRepository">' +
                                        '</div>' +
                                        '<div class="col-sm-1" style="text-align: right; padding: 0.7rem;">' +
                                            '<label>Label:</label>' +
                                        '</div>' +
                                        '<div class="col-sm-3">' +
                                            '<input key="wsRepoLabel" value="' + this.label + '" katana-change="assembler.checkWsLabel">' +
                                        '</div>' +
                                    '</div>' +
                                    '<br>' +
                                '</div>' +
                                '<div class="card-footer assembler-no-bg">' +
                                    '<div class="row" style="' + hideAvailability + '">' +
                                        '<div class="col-sm-1">' +
                                            '<i class="' +  wsAvailableIcon + ' assembler-icon-pos-right"></i>' +
                                        '</div>' +
                                        '<div class="col-sm-8 text-muted">' +
                                            wsAvailabvarext +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<br>';
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
        };
        return jsonObject;
    }
}

class dependency{
    constructor(data){
        if(!data || data === undefined){
            data = {};
        }
        if(data["@name"]){
            this.name = data["@name"];
        } else {
            this.name = "Enter Dependency Details";
        }
        if(!data["install"]){
            this.install = data["@install"].toLowerCase().trim();
        } else {
            this.install = "yes";
        }
        if(!data["@user"]){
            this.user = data["@user"].toLowerCase().trim();
        } else {
            this.user = "no"
        }
        this.version = data["version"];
        this.installed = data["installed"];
        this.matched = data["matched"];
        this.description = data["description"];
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var availabvarext = "";
        var installFunction = 'katana-click="assembler.installDependency"';
        if(this.installed){
            availabvarext = 'Available Version: ' + this.installed
        }
        var depSelect = "true";
        var installBtnText = "Install As Admin";
        if(this.user === "yes"){
            installBtnText = "Install As User";
        }
        var installBtnBgColor = "background-color: #4ea4e0; color: white;";
        var installBtnIcon = '<i class="fa fa-check" style="color: white" aria-hidden="true"></i>';
        if(this.install === "no"){
            depSelect = "false";
            installBtnText = "Install";
            installBtnBgColor = "background-color: white";
            installBtnIcon = "";
        }
        if(this.matched === "lower"){
            installBtnText = "Upgrade";
            installFunction = 'katana-click="assembler.upgradeDependency"';
            installBtnIcon = '<i class="fa fa-exclamation-triangle tan" aria-hidden="true"></i>';
            if(this.install === "yes"){
                installBtnBgColor = "background-color: #987150; color: white;";
                depSelect = "true";
                if(this.user === "yes"){
                    installBtnText = "Upgrade As Admin";
                }
                else {
                    installBtnText = "Upgrade As User";
                }
            }
        } else if (this.matched || this.matched === "higher") {
            installFunction = "";
            installBtnText = "Installed";
            installBtnIcon = '<i class="fa fa-check-circle skyblue" aria-hidden="true"></i>';
            depSelect = "false";
        }

        var html_contents = '<div style="padding: 1rem;">' +
                                '<div class="card border-secondary" style="width: 350px; height:190px; padding: 1rem;">' +
                                    '<div class="card-block">' +
                                        '<h4 class="card-title assembler-description">' + this.name +
                                            '<span class="assembler-description-text">' + this.description + '</span>' +
                                        '</h4>' +
                                        '<h6 class="card-subtitle mb-2 text-muted">Version: ' + this.version + '</h6><hr>' +
                                        '<h6 class="card-subtitle mb-2 text-muted">' + availabvarext + '&nbsp;</h6><br>' +
                                        '<button class="btn btn-success" ' + installFunction +
                                                 ' aria-selected="' + depSelect + '" style="' + installBtnBgColor + '">' +
                                            installBtnText + "&nbsp;" + installBtnIcon +
                                        '</button>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
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
        };
        return jsonObject;
    }
}

class toolsRepository{
    constructor(data){
        if(!data || data === undefined){
            data = {};
        }
        if(data["name"]){
            this.name = data["name"]
        } else {
            this.name = "Enter Repository Details";
        }
        if(data["@url"]){
            this.url = data["@url"]
        } else {
            this.url = "";
        }
        if(data["@clone"]){
            this.clone = data["@clone"].toLowerCase().trim();
        } else {
            this.clone = "yes";
        }
        if(data["@label"]){
            this.label = data["@label"]
        } else {
            this.label = "";
        }
        this.available = data["available"]
    }

    get domElement(){
        return this.formDomElement();
    }

    formDomElement() {
        var cloneRepoIcon = "fa fa-toggle-off grey";
        var cloneRepoSelected = "false";
        if(this.clone === "yes"){
            cloneRepoIcon = "fa fa-toggle-on skyblue";
            cloneRepoSelected = "true";
        }
        var repoAvailableIcon = "fa fa-times red";
        var repoAvailabvarext = "Repository Not Available";
        if(this.available){
            repoAvailableIcon = "fa fa-check-circle skyblue";
            repoAvailabvarext = "Repository Available";
        }
        var displayToolsFooter = "";
        if(this.url === ""){
            displayToolsFooter = "display: none";
        }
        var html_contents = '<div class="card border-secondary" style="padding: 1rem;">' +
                                '<div class="card-header assembler-no-bg">' +
                                    '<div class="row">' +
                                        '<div class="col-sm-1">' +
                                            '<i class="' + cloneRepoIcon + ' assembler-icon-pos-right"' +
                                            'aria-selected="' + cloneRepoIcon + '" katana-click="assembler.toggvaroolsClone" aria-hidden="true" '+
                                            'key="toolsRepoClone"></i>' +
                                        '</div>' +
                                        '<div class="col-sm-8">' +
                                            this.name +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="card-block" style="padding: 1rem;">' +
                                    '<div class="row">' +
                                        '<div class="col-sm-1" style="text-align: right; padding: 0.7rem;">' +
                                            '<label>URL:</label>' +
                                        '</div>' +
                                        '<div class="col-sm-5">' +
                                            '<input value="' + this.url + '" key="toolsRepo" katana-change="assembler.onchangeToolsUrl"' +
                                            'key="toolsRepo">' +
                                        '</div>' +
                                        '<div class="col-sm-1" style="text-align: right; padding: 0.7rem;">' +
                                            '<label>Label:</label>' +
                                        '</div>' +
                                        '<div class="col-sm-3">' +
                                            '<input value="' + this.label + '" katana-change="assembler.onchangeToolsLabel" ' +
                                                    'key="toolsRepoLabel" >' +
                                        '</div>' +
                                    '</div>' +
                                    '<div class="row">' +
                                    '</div>' +
                                    '<br>' +
                                '</div>' +
                                '<div class="card-footer assembler-no-bg">' +
                                    '<div class="row" style="' + displayToolsFooter + '">' +
                                        '<div class="col-sm-1">' +
                                            '<i class="' + repoAvailableIcon + ' assembler-icon-pos-right"></i>' +
                                        '</div>' +
                                        '<div class="col-sm-8 text-muted">' +
                                            repoAvailabvarext +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<br>';
        var $elem = $(html_contents);
        return $elem
    }

    get jsonObj() {
        return this.formJsonObj();
    }

    formJsonObj(){
        var jsonObject = {
            "@url": this.url,
            "@clone": this.clone,
            "@label": this.label,
        };
        return jsonObject;
    }
}