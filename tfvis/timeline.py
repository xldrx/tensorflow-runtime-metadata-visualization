#! /usr/bin/env python -u
# coding=utf-8
import os
from functools import lru_cache

import jinja2
import tfvis.load_data as load_data
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, Range1d, SingleIntervalTicker, WidgetBox, \
    HoverTool, CustomJS, Button
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

__author__ = 'xl'


class TimelineVisualization:
    @lru_cache()
    def get_tools(self):
        def boxed(content, tag='div'):
            return "<{tag} style='width: 600px; word-break: break-all; white-space: pre-wrap;'>{content}</{tag}>".format(
                content=content,
                tag=tag)

        hover = HoverTool(tooltips=[
            ("Name", boxed("@name")),
            ("op", boxed("@op")),
            ("Inputs", boxed("@inputs", 'pre')),
            ("Description", boxed("@description")),
            ("Duration (ms)", "@duration"),
            ("Start (ms)", "@start"),
            ("End (ms)", "@end"),
            # ("Details", "<pre style='width: 100px, white-space: pre-wrap;word-wrap: break-word;'>@details</pre>"),
        ], mode='mouse',
            point_policy='snap_to_data', attachment='vertical', show_arrow=False)

        tools = "xzoom_in,xzoom_out,xpan,xbox_zoom,xwheel_zoom,xwheel_pan,reset,undo,redo,crosshair".split(',')
        tools += [hover]

        return tools

    def timeline(self, device, max_x):
        data_source = self.make_datasource(device['events'])
        n_rows = device['n_rows']
        if n_rows == 0:
            n_rows = 1
        elif n_rows == 1:
            n_rows = 2
        name = device['name']
        tools = self.get_tools()

        p = figure(
            title="{}".format(name),
            plot_height=20 * n_rows + 60,
            plot_width=1200,
            tools=tools,
            sizing_mode='stretch_both',
            # sizing_mode='scale_width',
            active_scroll='xwheel_zoom'
        )
        # p.js_on_event('tap', callback)
        # p.toolbar.logo = None
        # p.toolbar_location = None
        p.hbar(
            left='start',
            right='end',
            y='height',
            color='color',
            height=0.85,
            source=data_source,
            hover_fill_alpha=0.5,
            line_join='round',
            line_cap='round',
            hover_line_color='red'
        )

        p.x_range = Range1d(0, max_x, bounds="auto")
        p.y_range = Range1d(0, n_rows)
        p.yaxis.visible = False
        p.ygrid.ticker = SingleIntervalTicker(interval=1)
        p.ygrid.grid_line_color = None
        p.ygrid.band_fill_alpha = 0.1
        p.ygrid.band_fill_color = "gray"

        update_all_ranges = CustomJS(
            args={
                'me': p,
            },
            code="""
                console.log(me);
                var start = me.x_range.start;
                var end = me.x_range.end;
                console.log(start, end);

                for (var model_id in me.document._all_models) {
                    model = me.document._all_models[model_id];
                    if (model.type=="Plot"){
                        console.log(model);
                        model.x_range.set('start', start);
                        model.x_range.set('end', end);
                    }
                    if (model.type=="Button"){
                        model.disabled = true;
                        if (model.label == " Sync"){
                            model.css_classes = ['xl-hidden'];
                        }
                    }

                }

            """)

        # p.x_range.js_on_change('start',update_all_ranges)

        button = Button(label=" Sync", width=20, button_type='primary', disabled=True)
        button.css_classes = ['xl-hidden']
        button.js_on_click(update_all_ranges)

        p.x_range.js_on_change('start', CustomJS(
            args={
                'button': button,
            },
            code="""
                console.log(button);
                button.disabled = false;
                button.css_classes = ['center-block', 'xl-sync'];
                """))

        return p, WidgetBox(button)
        # return p, WidgetBox(button, css_classes=list("col-sm-12 col-md-12 col-lg-12 col-xl-12".split(' ')))

    @staticmethod
    def make_datasource(device_data, base_row=0):
        def get_col(column_name, offset=None):
            if offset:
                return [item[column_name] + offset for item in device_data]
            else:
                return [item[column_name] for item in device_data]

        return ColumnDataSource(data=dict(
            duration=get_col("duration"),
            start=get_col("start"),
            end=get_col('end'),
            height=get_col('row', base_row + 0.5),
            color=get_col('color'),
            row=get_col('row', base_row),
            name=get_col('name'),
            description=get_col('description'),
            details=get_col('details'),
            op=get_col('op'),
            inputs=get_col('inputs'),
        ))

    @staticmethod
    def generate_html(plot):
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        script, div = components(plot)
        template_file = os.path.join(os.path.dirname(__file__), "timeline.template")
        with open(template_file) as fp:
            template_src = fp.read()

        template = jinja2.Template(template_src)
        html = template.render(
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
            custom_css=r"""
            .xl-hidden {
                visibility: hidden;
            }
            .xl-sync button:before{
                content: "\f021 ";
                display: inline-block;
                font: normal normal normal 14px/1 FontAwesome;
                font-size: inherit;
                text-rendering: auto;
                /*-webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                -webkit-animation: fa-spin 2s infinite linear;
                animation: fa-spin 2s infinite linear;*/
            }
            .bk-toolbar-box {
                position: fixed !important;
                z-index: 999999999;
            }
            .bk-toolbar-above{
                background-color: rgba(255, 255, 255, 0.85);
            }
            """,
            title="TensorFlow Timeline",
            custom_header='',
            custom_js=''
        )

        return encode_utf8(html)

    def visualize(self, run_metadata, output_file=None):
        data = load_data.get_data(run_metadata)
        # output_file("timeline.html")
        max_x = max([max([event['end'] for event in device['events']]) for device in data])
        plots = []
        for device in data:
            p = self.timeline(device, max_x=max_x)
            plots += [[p[0]], [p[1]]]

        all_plots = gridplot(
            *plots,
            toolbar_options={
                # 'tools': get_tools(),
                'logo': None,
                'merge_tools': True
            },
            # ncols=1,
            # sizing_mode='stretch_both'
            sizing_mode='scale_width'
            # responsive=True
        )

        result = self.generate_html(all_plots)

        if output_file:
            with open(output_file, "w") as fp:
                fp.write(result)
        else:
            return result