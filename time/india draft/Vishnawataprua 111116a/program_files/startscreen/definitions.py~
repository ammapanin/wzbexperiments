# Last updated: 2 May 2016
# Collecton of the definitions to create a Startscreen


## Transformation tuples are of the form
#  (("view_label", "data_label"), "data_name")

transform_enum = (("enum_name", "enum_id"), "enum_id")

## "standard" and "dynamic" are dictionaries of dropdown menus
# Each grouping consists of:
# "data_path" - path to data
# "column(s)" - -name of column to use for standard
#               -tuples of relations for dynamic
# "colnames": tuple of column names for dynamic
# "condition": header of column that will be used as a filter
# "transformations": a dictionary of transformation tuples
standard = {"enumerator": {"data_path": "enumerators.csv",
                           "column": "enum_name",
                           "transformations": transform_enum}
        }

dynamic = {"households": {"data_path": "household_listing_100516.csv",
                          "columns": (("taluk", "village"),
                                      ("village", "experiment_name"),
                                      ("experiment_name", "name")),
                          "colnames": ("taluk", "village",
                                       "household", "individual name"),
                          "condition": "comparison_task",
                          "saved_headings": ("taluk", "village", "tid", "vid",
                                             "wzb.hh.id", "wzb.ind.id", "name")
                      }
       }

definitions = {"standard": standard,
               "dynamic": dynamic}
