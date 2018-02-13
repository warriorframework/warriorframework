from django import template
from wapps.cases.cases_utils.defaults import inverted_on_errors, inverted_contexts, \
    inverted_impacts, inverted_runmodes, inverted_iteration_types

register = template.Library()

@register.filter(name='convert_runmodes')
def convert_runmodes(value):
    return inverted_runmodes()[value]


@register.filter(name='convert_on_errors')
def convert_on_errors(value):
    return inverted_on_errors()[value]


@register.filter(name='convert_iteration_types')
def convert_iteration_types(value):
    return inverted_iteration_types()[value]


@register.filter(name='convert_contexts')
def convert_contexts(value):
    return inverted_contexts()[value]


@register.filter(name='convert_impacts')
def convert_impacts(value):
    return inverted_impacts()[value]
