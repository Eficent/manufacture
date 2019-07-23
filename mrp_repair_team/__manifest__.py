# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Repair team",
    "summary": "Repair teams",
    "version": "11.0.1.0.1",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'mrp_repair',
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/repair_team_security.xml",
        "views/mrp_repair_view.xml",
        "views/mrp_repair_team_view.xml",
        "views/mrp_repair_type_view.xml",
        'views/res_users_view.xml',
    ],
}
