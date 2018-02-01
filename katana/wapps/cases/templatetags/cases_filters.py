from django import template

from utils.dict_utils import invert_dict

register = template.Library()


@register.filter(name='replace_char')
def replace_char(value, replace_with=""):
    return value.replace(" ", replace_with)


@register.filter(name='convert_runmodes')
def convert_runmodes(value):
    runmodes = {
        "Standard": "standard",
        "Run Multiple Times": "RMT",
        "Run Until Pass": "RUP",
        "Run Until Failure": "RUF"
    }
    runmodes.update(invert_dict(runmodes))
    return runmodes[value]


@register.filter(name='convert_on_errors')
def convert_on_errors(value):
    on_errors = {
        "Next": "next",
        "Abort": "abort",
        "Abort As Error": "abort_as_error",
        "Go To": "goto"
    }
    on_errors.update(invert_dict(on_errors))
    return on_errors[value]


@register.filter(name='convert_iteration_types')
def convert_iteration_types(value):
    iteration_types = {
        "Standard": "standard",
        "Once Per Case": "once_per_tc",
        "End Of Case": "end_of_tc"
    }
    iteration_types.update(invert_dict(iteration_types))
    return iteration_types[value]


@register.filter(name='convert_contexts')
def convert_contexts(value):
    contexts = {
        "Positive": "positive",
        "Negative": "negative"
    }
    contexts.update(invert_dict(contexts))
    return contexts[value]


@register.filter(name='convert_impacts')
def convert_impacts(value):
    impacts = {
        "Impact": "impact",
        "No Impact": "noimpact"
    }
    impacts.update(invert_dict(impacts))
    return impacts[value]
