# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp Bom Responsible',
    'summary': """
        Adds a responsible to the Bill of Materials which then will be 
        forwarded to the Manufacturing Order""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/manufacture',
    'depends': [
        'mrp'
    ],
    'data': [
        'views/mrp_bom_views.xml',
    ],
}
