/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class StaffRoleBadge extends Component {
    static template = "medisite_clinic.StaffRoleBadge";
    static props = {
        ...standardFieldProps,
    };

    get roleColorClass() {
        const role = this.props.record.data[this.props.name];
        const colorMap = {
            'nurse': 'bg-info',
            'doctor': 'bg-primary',
            'lab_tech': 'bg-warning text-dark',
            'pharmacist': 'bg-success',
            'paramedic': 'bg-danger',
            'admin': 'bg-dark',
            'reception': 'bg-secondary',
        };
        return colorMap[role] || 'bg-light text-dark';
    }

    get roleLabel() {
        const choices = this.props.record.fields[this.props.name].selection;
        const roleValue = this.props.record.data[this.props.name];
        const choice = choices.find(c => c[0] === roleValue);
        return choice ? choice[1] : roleValue;
    }
}

registry.category("fields").add("staff_role_badge", {
    component: StaffRoleBadge,
    supportedTypes: ["selection"],
});
