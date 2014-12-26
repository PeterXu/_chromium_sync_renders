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
    core/html/HTMLMediaElement.cpp
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

    url_request for mmt
-------------

    net/url_request/url_request_context_builder.cc
    net/url_request/ftp_protocol_handler.h
    net/url_request/file_protocol_handler.h
    net/url_request/http_protocol_handler.h

    URLRequestContext* URLRequestContextBuilder::Build() {
        job_factory->SetProtocolHandler("file", ..);
        job_factory->SetProtocolHandler("ftp", "..");
    }


    chrome/service/net/service_url_request_context_getter.cc
    net/url_request/url_request_context_getter.cc
    net/url_request/url_request_http_job.cc
    net/url_request/url_request_ftp_job.cc
    net/url_request/url_request_file_job.cc
    net/filter/filter.h

    net::URLRequestContext* ServiceURLRequestContextGetter::GetURLRequestContext() {
        net::URLRequestContextBuilder builder;
        ...
        builder.Build();
    }

    
    components/cronet/url_request_context_config.cc
    void URLRequestContextConfig::ConfigureURLRequestContextBuilder(net::URLRequestContextBuilder* context_builder) {
        context_builder->set_user_agent(user_agent);
        context_builder->SetSpdyAndQuicEnabled(enable_spdy, enable_quic);
        context_builder->set_quic_connection_options(..);
    }


    git grep kFtpScheme | grep -v "unittest\|android", git grep DISABLE_MMT_SUPPORT | grep -v "unittest\|android"
-------------
    chrome/browser/history/in_memory_url_index.cc
    void InitializeSchemeWhitelist(std::set<std::string>* whitelist) {
        whitelist->insert(std::string(url::kFtpScheme));
    }

    chrome/browser/web_applications/web_app.cc
    static const char* const kValidUrlSchemes[] = {kFtpScheme}

    content/browser/browser_url_handler_impl.cc
    static const char* const default_allowed_sub_schemes[] = {kFtpScheme}


    register new protocol handler
-----------
    chrome/browser/ui/browser.cc
    void RegisterProtocolHandler(content::WebContents* web_contents,
                                const std::string& protocol,
                                const GURL& url,
                                bool user_gesture) override;


ws/wss
======

    git grep wss | grep -v "test\|android\|ai:\|png\|py:\|html:\|gif\|JPG\|pem"
-----------

    chrome/browser/prerender/prerender_util.cc
    void ReportUnsupportedPrerenderScheme(const GURL& url);

