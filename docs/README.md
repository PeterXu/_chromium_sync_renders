prepare:
==========
    cmake       - 3.0+
    gcc         - 4.7+
    binutils    - 2.24+ 

start options
=============
    --enable-logging --v=1
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

code (WebKit)
=========
    CSS parser(CSSParser) is done by bison, implemented in CSSGrammar.y
    CSSParser::createStyleRule()


media (WebKit)
==============
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

    chrome/browser/profiles/profile_io_data.cc: add new protocol into it
    net/url_request/url_request_context_builder.cc: add new protocol into it

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


ffmpeg
======

    git grep OpenContext  | grep -v "unittest\|views\|OpenContextMenu"
------------
    media/filters/ffmpeg_demuxer.h
    implement FFmpegDemuxer

    media/filters/ffmpeg_glue.h
    implement FFmpegGlue and binds with FFmpegURLProtocol

    media/filters/blocking_url_protocol.h
    BlockingUrlProtocol implement FFmpegURLProtocol

    content/renderer/media/audio_decoder.cc
    media/cast/test/fake_media_source.h
    media/filters/in_memory_url_protocol.h
    InMemoryUrlProtocol implement FFmpegURLProtocol

 
html docs
===========
http://www.chromium.org/audio-video
http://www.chromium.org/developers/design-documents/inter-process-communication


chrome browser
==============
    html5 fullscreen:
        src/chrome/browser
            Browser(WebContentsDelegate)->FullscreenController->BrowserWindow->ui::WebVeiw(WasResized)
        src/content/browser: ViewHostMsg_ToggleFullscreen<Send>/ViewMsg_Resize(recevie)
            IPCs of renderer process ->RenderViewHostImpl(Send/receive)->WebContentsImpl

    ppapi
        pp::MessageLoop::GetCurrent()

    content/public/browser/site_instance.h
    content/browser/browsing_instance.h
        BrowserContext* browser_context();

    chrome/browser/extensions/api/tabs/tabs_api.cc
    extensions/browser/api/execute_code_function.cc
    extensions/browser/script_executor.h
        content::BrowserThread::PostTask

    chrome/browser/chrome_notification_types.h
    chrome/browser/ui/browser.h
    chrome/browser/ui/browser_commands.h
        Browser* OpenEmptyWindow(Profile* profile, HostDesktopType desktop_type);

    chrome/browser/profiles/profile.h
        static Profile* FromBrowserContext(content::BrowserContext* browser_context);
        static Profile* FromWebUI(content::WebUI* web_ui);
        
    chrome/browser/ui/browser_finder.h
    chrome/browser/chrome_main_browsertest.cc
    content/public/browser/web_contents.h
        browser()->tab_strip_model()->GetActiveWebContents()

    chrome/browser/fullscreen.h
        bool IsFullScreenMode();
    chrome/browser/ui/host_desktop.h
        HostDesktopType GetActiveDesktop();
    chrome/service/service_process.cc 
        ServiceProcess* g_service_process = NULL;
    chrome/browser/browser_process.h
        BrowserProcess* g_browser_process = NULL;


conent public api
=================
    content/public/browser/web_contents.h
    content/public/common/content_client.h
    content/public/browser/render_frame_host.h
        ContentClient* GetContentClient();
        static WebContents* FromRenderViewHost(const RenderViewHost* rvh);
        static WebContents* FromRenderFrameHost(RenderFrameHost* rfh);
        static RenderFrameHost* FromID(int render_process_id, int render_frame_id);

    content/public/browser/resource_request_info.h
        static const ResourceRequestInfo* ForRequest(const net::URLRequest* request);
        static bool GetRenderFrameForRequest(const net::URLRequest* request,int* render_process_id,int* render_frame_id);
        virtual int GetRouteID() const = 0;
        virtual int GetRenderFrameID() const = 0;

storage api
===========
    extensions/browser/api/storage/storage_frontend.h
    extensions/common/extension.h
    extensions/browser/extension_registry.h
    extensions/browser/extension_system.h
        ExtensionSystem* ExtensionSystem::Get(content::BrowserContext* context);
        ExtensionService* extension_service();

    chrome/browser/profiles/profile_manager.h
    chrome/browser/extensions/unpacked_installer.h
    chrome/browser/extensions/extension_browsertest.h
    chrome/browser/extensions/extension_service.h
        ExtensionBrowserTest::LoadExtensionWithInstallParam(..);
        UnpackedInstaller::Load(path);
        ExtensionSystem* ExtensionSystem::Get(content::BrowserContext* context);
        Extension* ExtensionService::GetExtensionById(id);


call stack
=========
    content/browser/loader/resource_dispatcher_host_impl.h
    content/browser/loader/resource_loader.cc - for one request(ResourceLoad) ...
    net/url_request/url_request_job_manager.cc
    net/url_request/url_request.cc - for one job(URLRequest)

    #0 0x7f1f255ddb9e base::debug::StackTrace::StackTrace()
    #1 0x7f1f25658435 logging::LogMessage::~LogMessage()
    #2 0x7f1f2d183020 ObserverListBase<>::AddObserver()
    #3 0x7f1f2d17b063 ObserverListThreadSafe<>::AddObserver()
    #4 0x7f1f2d17a635 base::PowerMonitor::AddObserver()
    #5 0x7f1f25cc19e9 net::URLRequestJob::URLRequestJob()
    #6 0x7f1f25cbd6eb net::URLRequestMmtJob::URLRequestMmtJob()
    #7 0x7f1f25c9fe8a net::MmtProtocolHandler::MaybeCreateJob()
    #8 0x7f1f25cc7d14 net::URLRequestJobFactoryImpl::MaybeCreateJobWithProtocolHandler()
    #9 0x7f1f25cc12e5 net::URLRequestInterceptingJobFactory::MaybeCreateJobWithProtocolHandler()
    #10 0x7f1f25cc12e5 net::URLRequestInterceptingJobFactory::MaybeCreateJobWithProtocolHandler()
    #11 0x7f1f25cc12e5 net::URLRequestInterceptingJobFactory::MaybeCreateJobWithProtocolHandler()
    #12 0x7f1f2480ae58 ProtocolHandlerRegistry::JobInterceptorFactory::MaybeCreateJobWithProtocolHandler()
    #13 0x7f1f25ccc5d9 net::URLRequestJobManager::CreateJob()
    #14 0x7f1f25ca807d net::URLRequest::BeforeRequestComplete()
    #15 0x7f1f25ca79df net::URLRequest::Start()
    #16 0x7f1f2a457edb content::ResourceLoader::StartRequestInternal()
    #17 0x7f1f2a457d7e content::ResourceLoader::StartRequest()
    #18 0x7f1f2a429e1e content::ResourceDispatcherHostImpl::StartLoading()
    #19 0x7f1f2a420a35 content::ResourceDispatcherHostImpl::BeginRequestInternal()
    #20 0x7f1f2a4256be content::ResourceDispatcherHostImpl::BeginRequest()
    #21 0x7f1f2a424037 content::ResourceDispatcherHostImpl::OnRequestResource()
    #22 0x7f1f2a44c716 _Z20DispatchToMethodImplIN7content26ResourceDispatcherHostImplEMS1_FviiRK23ResourceHostMsg_RequestEJiiS2_EJLm0ELm1ELm2EEEvPT_T0_RK5TupleIJDpT1_EE13IndexSequenceIJXspT2_EEE
    #23 0x7f1f2a44c625 _Z16DispatchToMethodIN7content26ResourceDispatcherHostImplEMS1_FviiRK23ResourceHostMsg_RequestEJiiS2_EEvPT_T0_RK5TupleIJDpT1_EE
    #24 0x7f1f2a432503 ResourceHostMsg_RequestResource::Dispatch<>()
    #25 0x7f1f2a423889 content::ResourceDispatcherHostImpl::OnMessageReceived()
    #26 0x7f1f2a45f6dd content::ResourceMessageFilter::OnMessageReceived()
    #27 0x7f1f2a21923d content::BrowserMessageFilter::Internal::DispatchMessage()
    #28 0x7f1f2a2187fe content::BrowserMessageFilter::Internal::OnMessageReceived()
    #29 0x7f1f266fe2bc IPC::(anonymous namespace)::TryFiltersImpl()
    #30 0x7f1f266fe232 IPC::MessageFilterRouter::TryFilters()
    #31 0x7f1f266da98b IPC::ChannelProxy::Context::TryFilters()
    #32 0x7f1f266dab8f IPC::ChannelProxy::Context::OnMessageReceived()
    #33 0x7f1f266e3945 IPC::internal::ChannelReader::DispatchInputData()
    #34 0x7f1f266e348b IPC::internal::ChannelReader::ProcessIncomingMessages()
    #35 0x7f1f266d4313 IPC::ChannelPosix::OnFileCanReadWithoutBlocking()
    #36 0x7f1f266d4502 IPC::ChannelPosix::OnFileCanReadWithoutBlocking()
    #37 0x7f1f255b903d base::MessagePumpLibevent::FileDescriptorWatcher::OnFileCanReadWithoutBlocking()
    #38 0x7f1f255ba564 base::MessagePumpLibevent::OnLibeventNotification()
    #39 0x7f1f2576d8b0 event_process_active
    #40 0x7f1f2576cea2 event_base_loop
    #41 0x7f1f255ba8e4 base::MessagePumpLibevent::Run()
    #42 0x7f1f2566c342 base::MessageLoop::RunHandler()
    #43 0x7f1f256b44b4 base::RunLoop::Run()
    #44 0x7f1f2566ba81 base::MessageLoop::Run()
    #45 0x7f1f2570d189 base::Thread::Run()
    #46 0x7f1f2a28da16 content::BrowserThreadImpl::IOThreadRun()
    #47 0x7f1f2a28dbfd content::BrowserThreadImpl::Run()
    #48 0x7f1f2570d3ea base::Thread::ThreadMain()
    #49 0x7f1f256fb74c base::(anonymous namespace)::ThreadFunc()
    #50 0x7f1f1d557e9a start_thread
    #51 0x7f1f1b7bb2ed clone


http request
=============
    GetResponseCode
    GetResponseInfo
    GetFullRequestHeaders
    GetTotalReceivedBytes
    request_->set_received_response_content_length
    GetResponseHeaders

    content/browser/service_worker/service_worker_url_request_job.cc: stream_->ReadRawData();
    content/browser/streams/stream_url_request_job.cc: stream_->ReadRawData();
    net/url_request/url_request_job.cc: ReadRawDataHelper/ReadRawDataHelper/ReadRawData

Read media
===========
    content/browser/loader/buffered_resource_handler.cc
    content/browser/loader/async_resource_handler.cc   => update data buffer, kMaxAllocationSize
    media/blink/buffered_resource_loader.h

    ResourceLoader::ReadMore
    #0 0x7f7c2d48cb9e base::debug::StackTrace::StackTrace()
    #1 0x7f7c2d507435 logging::LogMessage::~LogMessage()
    #2 0x7f7c2db6d614 net::URLRequestMmtJob::ReadRawData()
    #3 0x7f7c2db718e6 net::URLRequestJob::ReadRawDataHelper()
    #4 0x7f7c2db71481 net::URLRequestJob::Read()
    #5 0x7f7c2db58d96 net::URLRequest::Read()
    #6 0x7f7c32310014 content::ResourceLoader::ReadMore()
    #7 0x7f7c3230e40a content::ResourceLoader::StartReading()
    #8 0x7f7c3230d853 content::ResourceLoader::OnResponseStarted()
    #9 0x7f7c2db59695 net::URLRequest::NotifyResponseStarted()
    #10 0x7f7c2db740dd net::URLRequestJob::NotifyHeadersComplete()
    #11 0x7f7c2db6e729 net::URLRequestMmtJob::DidStart()
    #12 0x7f7c2db70189 base::internal::RunnableAdapter<>::Run()
    #13 0x7f7c2db700f8 base::internal::InvokeHelper<>::MakeItSo()
    #14 0x7f7c2db7008c base::internal::Invoker<>::Run()
    #15 0x7f7c2c2c1a5e base::Callback<>::Run()
    #16 0x7f7c2d6014a9 base::debug::TaskAnnotator::RunTask()
    #17 0x7f7c2d51b878 base::MessageLoop::RunTask()
    #18 0x7f7c2d51b9db base::MessageLoop::DeferOrRunPendingTask()
    #19 0x7f7c2d51bbc5 base::MessageLoop::DoWork()
    #20 0x7f7c2d4696a3 base::MessagePumpLibevent::Run()
    #21 0x7f7c2d51b342 base::MessageLoop::RunHandler()
    #22 0x7f7c2d5634b4 base::RunLoop::Run()
    #23 0x7f7c2d51aa81 base::MessageLoop::Run()
    #24 0x7f7c2d5bc189 base::Thread::Run()
    #25 0x7f7c32140df6 content::BrowserThreadImpl::IOThreadRun()
    #26 0x7f7c32140fdd content::BrowserThreadImpl::Run()
    #27 0x7f7c2d5bc3ea base::Thread::ThreadMain()
    #28 0x7f7c2d5aa74c base::(anonymous namespace)::ThreadFunc()
    #29 0x7f7c25406e9a start_thread
    #30 0x7f7c2366a2ed clone


media state
======
    third_party/WebKit/public/platform/WebMediaPlayer.h

    OnFindStreamInfoDone => GetFFmpegStream => OnAudioRendererInitializeDone => OnVideoRendererInitializeDone


load extensions
===============
    ExtensionLoaderHandler::LoadUnpackedExtensionImpl():
    chrome/browser/ui/webui/extensions/extension_loader_handler.cc

    web_ui register event "extensionLoaderLoadUnpacked" by chrome.send('extensionLoaderLoadUnpacked');
    chrome/browser/ui/webui/extensions/extension_loader_handler.cc


cast a/v stream
===============
    chrome/common/extensions/api/cast_streaming_session.idl
    chrome/common/extensions/api/cast_streaming_rtp_stream.idl
    chrome/common/extensions/api/cast_streaming_udp_transport.idl

    chrome/common/extensions/api/_permission_features.json
    chrome/renderer/extensions/cast_streaming_native_handler.cc

    CreateCastSession/DestroyCastRtpStream/StartCastRtpStream/SetDestinationCastUdpTransport
    chrome/renderer/media/cast_rtp_stream.cc


    for WebKit
    WebKit/Source/platform/RuntimeEnabledFeatures.in
    WebKit/Source/core/html/HTMLMediaElement.h

