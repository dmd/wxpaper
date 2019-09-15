/******************************************************/
//       THIS IS A GENERATED FILE - DO NOT EDIT       //
/******************************************************/

#include "application.h"
#line 1 "/Users/ddrucker/wxpaper/particle/src/main.ino"
#include "epd.h"

void setup(void);
int fontsize(String x);
int clear(String x);
int rect(String coords);
int img(String imginfo);
int text(String textinfo);
int update(String x);
void loop();
#line 3 "/Users/ddrucker/wxpaper/particle/src/main.ino"
void setup(void)
{
    epd_init();
    epd_wakeup();
    epd_set_memory(MEM_TF);
    epd_set_color(BLACK, WHITE);
    epd_set_en_font(ASCII32);
    epd_clear();
    epd_disp_string("waiting for update...", 300, 300);
    epd_update();
    Time.zone(-4);
    Particle.function("fontsize", fontsize);
    Particle.function("clear", clear);
    Particle.function("img", img);
    Particle.function("text", text);
    Particle.function("update", update);
    Particle.function("rect", rect);
}

int fontsize(String x)
{
    if (x == "32")
        epd_set_en_font(ASCII32);
    if (x == "48")
        epd_set_en_font(ASCII48);
    if (x == "64")
        epd_set_en_font(ASCII64);
}

int clear(String x)
{
    epd_clear();
}

int rect(String coords)
{
    int x0, y0, x1, y1;
    int c1 = coords.indexOf('|');
    int c2 = coords.indexOf('|', c1 + 1);
    int c3 = coords.indexOf('|', c2 + 1);
    x0 = coords.substring(0, c1).toInt();
    y0 = coords.substring(c1 + 1, c2).toInt();
    x1 = coords.substring(c2 + 1, c3).toInt();
    y1 = coords.substring(c3 + 1).toInt();
    epd_draw_rect(x0, y0, x1, y1);
}

int img(String imginfo)
{
    int x, y;
    String img;

    int c1 = imginfo.indexOf('|');
    int c2 = imginfo.indexOf('|', c1 + 1);
    img = imginfo.substring(0, c1);
    x = imginfo.substring(c1 + 1, c2).toInt();
    y = imginfo.substring(c2 + 1).toInt();
    epd_disp_bitmap(img.c_str(), x, y);
}

int text(String textinfo)
{
    int x, y;
    String text;

    int c1 = textinfo.indexOf('|');
    int c2 = textinfo.indexOf('|', c1 + 1);
    text = textinfo.substring(0, c1);
    x = textinfo.substring(c1 + 1, c2).toInt();
    y = textinfo.substring(c2 + 1).toInt();
    epd_disp_string(text, x, y);
}

int update(String x)
{
    epd_update();
}

void loop()
{
    delay(10000);
}