"""
Security Group tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from collections import namedtuple

from pyramid import testing

from koala.forms.securitygroups import SecurityGroupForm, SecurityGroupDeleteForm
from koala.views import TaggedItemView
from koala.views.panels import form_field_row, tag_editor, securitygroup_rules
from koala.views.securitygroups import SecurityGroupsView, SecurityGroupView

from tests import BaseViewTestCase, BaseFormTestCase


class SecurityGroupsViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = SecurityGroupsView(request)

    def test_get_json_view(self):
        self.assertEqual(self.view.get_items(), [])
        self.assertEqual(self.view.securitygroups_json(), dict(results=[]))

    def test_landing_page_view(self):
        lpview = self.view.securitygroups_landing()
        self.assertEqual(lpview.get('prefix'), '/securitygroups')
        self.assertEqual(lpview.get('display_type'), 'tableview')  # Security group defaults to table view
        self.assertTrue('/securitygroups/json' in lpview.get('json_items_endpoint'))  # JSON endpoint
        self.assertEqual(lpview.get('initial_sort_key'), 'name')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('name' in filter_keys)
        self.assertTrue('description' in filter_keys)
        self.assertTrue('tags' in filter_keys)  # Object has tags


class SecurityGroupViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = SecurityGroupView(request)

    def test_is_tagged_view(self):
        """Security group view should inherit from TaggedItemView"""
        self.assertTrue(isinstance(self.view, TaggedItemView))

    def test_item_view(self):
        itemview = SecurityGroupView(self.request).securitygroup_view()
        self.assertEqual(itemview.get('security_group'), None)
        self.assertTrue(itemview.get('securitygroup_form') is not None)
        self.assertTrue(itemview.get('delete_form') is not None)

    def test_update_view(self):
        updateview = SecurityGroupView(self.request).securitygroup_update()
        self.assertEqual(updateview.get('security_group'), None)

    def test_delete_view(self):
        deleteview = SecurityGroupView(self.request).securitygroup_delete()
        self.assertTrue(deleteview is not None)


class SecurityGroupFormTestCase(BaseFormTestCase):
    form_class = SecurityGroupForm
    request = testing.DummyRequest()
    security_group = None
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('description')

    def test_field_validators(self):
        self.assert_max_length('description', 255)

    def test_name_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.name)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)

    def test_description_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.description)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is not None)


class SecurityGroupPanelsTestCase(BaseViewTestCase):
    form_class = SecurityGroupForm
    request = testing.DummyRequest()
    security_group = None
    form = form_class(request)

    def test_panel_readonly_html_attr(self):
        """Test if we set the proper HTML attr when passing a 'readonly' kwarg to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.description, readonly='readonly')
        self.assertTrue('readonly' in fieldrow.get('html_attrs').keys())

    def test_add_form(self):
        """Form field data should be empty if new item (i.e. security_group is None)"""
        self.assertTrue(self.form.name.data is None)
        self.assertTrue(self.form.description.data is None)

    def test_tag_editor_panel(self):
        tageditor = tag_editor(None, self.request, tags=[])
        self.assertEqual(tageditor.get('tags'), {})
        self.assertEqual(tageditor.get('tags_json'), '{}')

    def test_rules_editor_panel(self):
        Rule = namedtuple('Rule', ['ip_protocol', 'from_port', 'to_port', 'grants'])
        Grant = namedtuple('Grant', ['name', 'owner_id', 'group_id', 'cidr_ip'])
        rules = [
            Rule(ip_protocol='tcp', from_port=80, to_port=80,
                 grants=[Grant(name=None, owner_id='12345678', group_id=None, cidr_ip='127.0.0.1/32')])
        ]
        ruleseditor = securitygroup_rules(None, self.request, rules=rules)
        rules_output = [{
            'to_port': 80,
            'grants': [{'owner_id': '12345678', 'group_id': None, 'cidr_ip': '127.0.0.1/32', 'name': None}],
            'ip_protocol': 'tcp',
            'from_port': 80
        }]
        self.assertEqual(ruleseditor.get('rules'), rules_output)
        self.assertTrue(ruleseditor.get('icmp_choices') is not None)


class DeleteFormTestCase(BaseFormTestCase):
    form_class = SecurityGroupDeleteForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

