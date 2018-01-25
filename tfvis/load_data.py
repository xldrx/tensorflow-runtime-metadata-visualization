#! /usr/bin/env python -u
# coding=utf-8
import random
import re

__author__ = 'xl'


def set_row(events):
    rows = []
    for event in sorted(events, key=lambda x: x['start']):
        assigned = False
        for i, row in enumerate(rows):
            if row <= event['start']:
                event['row'] = i
                rows[i] = event['end']
                assigned = True
                break
        if not assigned:
            event['row'] = len(rows)
            rows.append(event['end'])
    return len(rows)


def set_color(events):
    for event in events:
        rand = random.Random(event['op'])
        event['color'] = "#%02x%02x%02x" % (rand.randint(0, 256), rand.randint(0, 256), rand.randint(0, 256))


def _parse_op_label(label):
    """Parses the fields in a node timeline label."""
    # Expects labels of the form: name = op(arg, arg, ...).
    match = re.match(r'(.*) = (.*)\((.*)\)', label)
    if match is None:
        return 'unknown', 'unknown', []
    nn, op, inputs = match.groups()
    if not inputs:
        inputs = []
    else:
        inputs = inputs.split(', ')
    return nn, op, inputs


def set_op(events):
    for event in events:
        _, op, inputs = _parse_op_label(event['description'])
        if op == "unknown":
            op = event['name']
            inputs = ""
        event['op'] = op
        event['inputs'] = "\n\n".join(inputs)


def process_device(device_name, node_stats, base_time):
    device_events = []

    for node in node_stats:
        device_events.append(dict(
            start=(node.all_start_micros - base_time)/1000,
            end=(max(node.all_end_rel_micros, 1) + node.all_start_micros - base_time)/1000,
            duration=node.all_end_rel_micros/1000,
            name=node.node_name,
            description=node.timeline_label,
            details=str(node).replace("\n", "\n\n")
        ))
    set_op(device_events)
    set_color(device_events)
    n_rows = set_row(device_events)

    return dict(
        name=device_name,
        n_rows=n_rows,
        events=device_events
    )


def get_data(run_metadata):
    stats = run_metadata.step_stats
    events = []

    base_time = min([min([node.all_start_micros for node in device.node_stats]) for device in stats.dev_stats])
    for device in stats.dev_stats:
        device_name = device.device
        event = process_device(device_name,
                               [node for node in device.node_stats if not node.node_name.startswith("AR")],
                               base_time)
        events.append(event)

        event = process_device("{} (All Reduce)".format(device_name),
                               [node for node in device.node_stats if node.node_name.startswith("AR")],
                               base_time)
        if event['events']:
            events.append(event)

    events.sort(key=lambda x: x['name'])
    return events
