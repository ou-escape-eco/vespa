from django.shortcuts import render

from django.views.generic.base import TemplateView


class AboutView(TemplateView):
    template_name='waspstatic/about.html'

    def get_context_data(self, **kwargs):
        return {
            'gallery_north': [
                {'src': 'images/picture 135.jpg', 'caption': 'SuperWASP-N'},
                {'src': 'images/ingobservatory.jpg', 'caption': 'ING observatory range'},

                {'src': 'gallery/images/picture_057.jpg', 'caption': 'Construction of SuperWASP-N'},
                {'src': 'gallery/images/picture_059.jpg', 'caption': 'Assembly of housing'},
                {'src': 'gallery/images/picture_072.jpg'},
                {'src': 'gallery/images/picture_112.jpg', 'caption': 'Delivery of the mount'},

                {'src': 'gallery/images/picture_124.jpg', 'caption': 'Location on ING site'},
                {'src': 'gallery/images/picture_127.jpg'},
                {'src': 'gallery/images/picture_138.jpg'},
                {'src': 'gallery/images/picture_160.jpg', 'caption': 'The WASP cameras'},

                {'src': 'gallery/images/picture_161.jpg'},
                {'src': 'gallery/images/picture_162.jpg', 'caption': 'Weather station'},
                {'src': 'gallery/images/picture_168.jpg'},
                {'src': 'gallery/images/picture_188.jpg', 'caption': 'Camera mount'},

                {'src': 'gallery/images/picture_190.jpg', 'caption': ''},
                {'src': 'gallery/images/M42closelab.gif', 'caption': 'Orion nebula'},
                {'src': 'gallery/images/M31close.gif', 'caption': 'M31'},
                {'src': 'gallery/images/Figm101exp10zm.gif', 'caption': 'M101'},

                {'src': 'gallery/images/Figm67exp3zm.gif', 'caption': 'M67'},
                {'src': 'gallery/images/Figm51exp30zm.gif', 'caption': 'M51'},
                {'src': 'gallery/images/sw3.jpg', 'caption': 'Comet C/2001 Q4 (NEAT)'},
                {'src': 'gallery/images/Figm44zm.gif', 'caption': 'M44'},

                {'src': 'gallery/images/Figm42exp0_5.gif', 'caption': 'M42'},
                {'src': 'gallery/images/Figm31exp3zm.gif', 'caption': 'M31'},
                {'src': 'gallery/images/Figcometm33.gif', 'caption': 'M33'},
                {'src': 'gallery/images/Figcometzm.gif'},
            ],
            'gallery_south': [
                {'src': 'images/saao.jpg', 'caption': 'SuperWASP-S at SAAO'},
                {'src': 'images/moonlight.jpg', 'caption': 'SuperWASP-S'},

                {'src': 'gallery2/images/img_0595.jpg'},
                {'src': 'gallery2/images/img_0603.jpg'},
                {'src': 'gallery2/images/img_0605.jpg'},
                {'src': 'gallery2/images/img_0645.jpg'},

                {'src': 'gallery2/images/img_0655.jpg'},
                {'src': 'gallery2/images/img_0659.jpg'},
                {'src': 'gallery2/images/img_0662.jpg'},
                {'src': 'gallery2/images/img_0671.jpg'},

                {'src': 'gallery2/images/img_0680.jpg'},
                {'src': 'gallery2/images/img_0697.jpg'},
                {'src': 'gallery2/images/img_0702.jpg'},
                {'src': 'gallery2/images/img_0703.jpg'},

                {'src': 'gallery2/images/img_0716.jpg'},
                {'src': 'gallery2/images/img_0723.jpg'},
                {'src': 'gallery2/images/img_0727.jpg'},
                {'src': 'gallery2/images/img_0737.jpg'},

                {'src': 'gallery2/images/img_0745.jpg'},
                {'src': 'gallery2/images/img_0765.jpg'},
                {'src': 'gallery2/images/img_0767.jpg'},
                {'src': 'gallery2/images/img_0771.jpg'},

                {'src': 'gallery2/images/img_0775.jpg'},
                {'src': 'gallery2/images/img_0785.jpg'},
                {'src': 'gallery2/images/img_0786.jpg'},
                {'src': 'gallery2/images/img_0793.jpg'},

                {'src': 'gallery2/images/img_0796.jpg'},
                {'src': 'gallery2/images/img_0804.jpg'},
                {'src': 'gallery2/images/img_0811.jpg'},
                {'src': 'gallery2/images/img_0815.jpg'},

                {'src': 'gallery2/images/img_0819.jpg'},
                {'src': 'gallery2/images/img_0839.jpg'},
                {'src': 'gallery2/images/img_0890.jpg'},
                {'src': 'gallery2/images/img_0895.jpg'},

                {'src': 'gallery2/images/img_0882.jpg'},
                {'src': 'gallery2/images/img_0989.jpg'},
                {'src': 'gallery2/images/img_0990.jpg'},
                {'src': 'gallery2/images/jupiter2.jpg'},
            ]
        }