"""Module that describes all utility functions for Simplepath."""


def convert_object_to_dict(data_object):
    """Convert all of the non-function attributes of an object into
       a dictionary.
    Args:
        data_object(object): any Python object
    Returns:
        The dictionary representation of all fields in the Python object.
    """

    if hasattr(data_object, "__dict__"):
        object_dict = vars(data_object).copy()
        for attrib_name, attrib_val in object_dict.items():
            if isinstance(attrib_val, tuple):
                object_dict[attrib_name] = [convert_object_to_dict(element)
                                            for element in attrib_val]
                object_dict[attrib_name] = tuple(object_dict[attrib_name])
            elif isinstance(attrib_val, list):
                object_dict[attrib_name] = [convert_object_to_dict(element)
                                            for element in attrib_val]
            elif isinstance(attrib_val, dict):
                object_dict[attrib_name] = \
                    {key: convert_object_to_dict(attrib_val[key])
                     for key in attrib_val}
            else:
                # This case assumes that attrib_val is a
                # non-iterable object.
                object_dict[attrib_name] = \
                    convert_object_to_dict(attrib_val)

        return object_dict
    else:
        return data_object
