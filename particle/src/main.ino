#include "epd.h"
#define SERVER_IP         \
    {                     \
        168, 235, 83, 233 \
    }
#define SERVER_PORT 33223
#define TIMEOUT_INITIAL_RESPONSE 5000
#define TIMEOUT_RESPONSE_READ 5000
#define RECONNECT_DELAY 3000

TCPClient client;

void setup(void)
{
    Particle.function("fontsize", fontsize);
    Particle.function("clear", clear);
    Particle.function("img", img);
    Particle.function("text", text);
    Particle.function("update", update);
    Particle.function("rect", rect);
    Particle.function("deepsleep", deepsleep);
    Particle.function("wake", wake);
    Particle.function("stop", stop);

    epd_init();
    epd_wakeup();
    epd_set_memory(MEM_TF);
    epd_set_color(BLACK, WHITE);
    epd_set_en_font(ASCII32);
    epd_clear();
    epd_disp_string("Requesting weather update.", 300, 300);
    epd_disp_string("I will wait 3 minutes, then sleep for 30 minutes.", 300, 350);
    epd_update();
    Time.zone(-4);

    TCPClient client;
    byte ip[] = SERVER_IP;
    client.connect(ip, SERVER_PORT);
    if (client.connected())
    {
        client.println("GET /pushmeplease HTTP/1.0");
        client.println();
        client.stop();
    }
    else
    {
        epd_disp_string("ERROR: Failed to connect to push server.", 300, 400);
        epd_update();
    }

    // if we're here, we successfully sent a push request, which should put us to sleep.
    // we need to wait for the push.
    delay(3 * 60 * 1000); // 3 minutes in ms

    // we should not reach this -- we should have been put to sleep by now.
    epd_disp_string("ERROR: Never received push. Going to sleep.", 300, 450);
    epd_update();
    delay(5 * 1000); // 5 seconds in ms 
    epd_enter_stopmode();
    System.sleep(SLEEP_MODE_DEEP, 30 * 60); // 30 minutes in sec
}

int deepsleep(String seconds)
{
    epd_enter_stopmode();
    System.sleep(SLEEP_MODE_DEEP, seconds.toInt());
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

int wake(String x)
{
    epd_wakeup();
}

int clear(String x)
{
    epd_clear();
}

int stop(String x)
{
    epd_enter_stopmode();
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
