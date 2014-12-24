prepare:
==========
    cmake       - 3.0+
    gcc         - 4.7+
    binutils    - 2.24+ 

start options
=============
    -no-sandbox, -test-sandbox
    -enable-logging, -disable-logging
    -debug-print

    -playback-mode
    -no-events
    -hide-icons
    -make-default-browser

    -disable-dev-tools, -always-enable-dev-tools
    -disable-javascript
    -disable-java
    -disable-plugins
    -safe-plugins
    -new-http

    -single-process
    -process-per-tab
    -process-per-site
    -in-process-plugins

code
=========
    CSS parser(CSSParser) is done by bison, implemented in CSSGrammar.y
    CSSParser::createStyleRule()


media
=========
1. core/html/HTMLMediaElement.cpp
    OwnPtr<MediaPlayer> m_player;
    static bool canLoadURL(const KURL& url, const ContentType& contentType, const String& keySystem);
    void HTMLMediaElement::loadResource(const KURL& url, ContentType& contentType, const String& keySystem);

    
    ### register stream url
    URLRegistry* HTMLMediaElement::s_mediaStreamRegistry = 0;
    void HTMLMediaElement::setMediaStreamRegistry(URLRegistry* registry) {s_mediaStreamRegistry = registry;}
    bool HTMLMediaElement::isMediaStreamURL(const String& url) {
        return s_mediaStreamRegistry ? s_mediaStreamRegistry->contains(url) : false;
    }

    modules/mediastream/MediaStreamRegistry.h/cpp
    HTMLMediaElement::setMediaStreamRegistry(this);


    ### process protocols, ws://, http://
    platform/network/WebSocketHandshakeRequest.h
    platform/network/HTTPRequest.h 
    platform/mediastream/
    platform/weborigin/SchemeRegistry.h: registerURLSchemeAsLegacy()

    ### process url
    url/gurl.cc


ftp/http/file:// 
===============
1. net/url_request/url_request_context_builder.cc
    URLRequestContext* URLRequestContextBuilder::Build() {
        job_factory->SetProtocolHandler("file", ..);
        job_factory->SetProtocolHandler("ftp", "..");
    }


2. chrome/service/net/service_url_request_context_getter.cc
   net/url_request/url_request_context_getter.cc
   net/url_request/url_request_http_job.cc
   net/filter/filter.h
    net::URLRequestContext* ServiceURLRequestContextGetter::GetURLRequestContext() {
        net::URLRequestContextBuilder builder;
        ...
        builder.Build();
    }

3. components/cronet/url_request_context_config.cc
    void URLRequestContextConfig::ConfigureURLRequestContextBuilder(net::URLRequestContextBuilder* context_builder) {
        context_builder->set_user_agent(user_agent);
        context_builder->SetSpdyAndQuicEnabled(enable_spdy, enable_quic);
        context_builder->set_quic_connection_options(..);
    }


