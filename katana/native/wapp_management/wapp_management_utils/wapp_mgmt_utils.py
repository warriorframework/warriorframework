import copy
from distutils.version import LooseVersion


def get_version_list(versions, existing_versions):
    """
    :param versions: comma separated version list.
        Eg: warrior-3.2.0, warrior-3.1.0::warrior-3.7.0, :warrior3.6.0
    :param existing_versions: List/Set of existing versions:
        [warrior-3.1.0, warrior-3.1.1, warrior-3.2.0 ...]
    :return:
        individual: List of versions
            Eg: [warrior-3.1.0, warrior-3.1.1, warrior-3.2.0 ...]
        bounds: range of versions
            Eg: [{"upper": "warrior-3.7.0", "lower": "warrior-3.4.0"}, {"upper": "warrior-3.2.0"}]
        errors: Boolean if any errors occurred during evaluation.
    """
    bounds = []
    individual = []
    version_list = [el.strip() for el in versions.split(',') if el.strip() != ""]
    err_msg = "-- An Error Occurred -- {0} is not a valid Warrior version. Valid Warrior versions are: {1}"
    errors = False
    for el in version_list:
        bound = {}
        if el.startswith(":"):
            el = el[1:].strip()
            if el in existing_versions:
                bound["upper"] = el
                bounds.append(copy.deepcopy(bound))
            else:
                print err_msg.format(el, ', '.join(existing_versions))
                errors = True
        elif "::" in el:
            el_list = el.split("::")
            if el_list[1].strip() in existing_versions:
                bound["upper"] = el_list[1]
                if el_list[0].strip() in existing_versions:
                    bound["lower"] = el_list[0]
                else:
                    print err_msg.format(el, ', '.join(existing_versions))
                    errors = True
            else:
                print err_msg.format(el, ', '.join(existing_versions))
                errors = True
            if len(bound.keys()) == 2:
                bounds.append(copy.deepcopy(bound))
        else:
            if el in existing_versions:
                individual.append(el)
            else:
                print err_msg.format(el, ', '.join(existing_versions))
                errors = True
    return individual, bounds, errors


def check_against_version_list(version, version_list, version_bounds):
    """
    :param version: version to be verified
    :param version_list: List of versions
            Eg: [warrior-3.1.0, warrior-3.1.1, warrior-3.2.0 ...]
    :param version_bounds: range of versions
            Eg: [{"upper": "warrior-3.7.0", "lower": "warrior-3.4.0"}, {"upper": "warrior-3.2.0"}]
    :return:
        status: Boolean. True if version is valid, False if not.
    """
    status = False
    for el in version_list:
        if version == el:
            status = True
            break
    if not status:
        for bound in version_bounds:
            if LooseVersion(version) <= LooseVersion(bound["upper"]):
                if "lower" in bound:
                    if LooseVersion(version) >= LooseVersion(bound["lower"]):
                        status = True
                        break
                else:
                    status = True
                    break
    return status
