package org.example.duui;

import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;
import org.apache.commons.compress.compressors.CompressorException;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.cas.CASException;
import org.apache.uima.fit.factory.AnalysisEngineFactory;
import org.apache.uima.fit.factory.JCasFactory;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.cas.FSArrayList;
import org.apache.uima.resource.ResourceInitializationException;
import org.apache.uima.util.InvalidXMLException;
import org.example.duui.model.uima.VideoBase64;
import org.texttechnologylab.DockerUnifiedUIMAInterface.DUUIComposer;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIDockerDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIRemoteDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUISwarmDriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.driver.DUUIUIMADriver;
import org.texttechnologylab.DockerUnifiedUIMAInterface.io.writer.TTLabXmiWriter;
import org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaContext;
import org.texttechnologylab.DockerUnifiedUIMAInterface.lua.LuaConsts;
import org.texttechnologylab.DockerUnifiedUIMAInterface.pipeline_storage.sqlite.DUUISqliteStorageBackend;
import org.xml.sax.SAXException;


import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;

public class DUUILoader {

    private int timeout;
    private int workers;
    private JCas cas;

    private String videoPath = "src/main/resources/qvijck-source.mp4";

    private String outputPath = "src/main/resoutces/output";

    public DUUILoader() {
        workers = 2;
        timeout = 10000;
    }

    private void loadCas() {
        try {
            cas = JCasFactory.createJCas();
            String videoName = "qvijck-source";
            Path videoPath = Path.of("src/main/resources/"+ videoName +".mp4");
            byte[] bytes = Files.readAllBytes(videoPath);

            DocumentMetaData metaData = DocumentMetaData.create(cas);
            metaData.setDocumentTitle(videoName);
            metaData.setDocumentUri(videoPath.toString());
            metaData.setCollectionId(videoName);

            StringBuilder sb = new StringBuilder();
            String base64 = Base64.getEncoder().encodeToString(bytes);
            VideoBase64 request = new VideoBase64(cas);
            request.setBase64Video(base64);
            request.setMetaData(metaData);
            request.addToIndexes();
            sb.append(request);
            cas.setDocumentText(sb.toString());

            cas.setDocumentLanguage("en");

        } catch (ResourceInitializationException e) {
            throw new RuntimeException(e);
        } catch (CASException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void process2() throws Exception {
        DUUIComposer composer = new DUUIComposer()
                .withSkipVerification(true)
                .withLuaContext(new DUUILuaContext().withJsonLibrary());
        composer.addDriver(new DUUIDockerDriver());
        composer.add(new DUUIDockerDriver.Component("docker.texttechnologylab.org/gnfinder:latest")
                .withParameter("model", "yannickheinrich/video-diarization")
                .withParameter("selection", "text")
                .withImageFetching());
        composer.run(cas);
    }

    private void process() throws Exception {
        DUUILuaContext context = LuaConsts.getJSON();
        DUUISqliteStorageBackend sqlite = new DUUISqliteStorageBackend("loggingSQlite.db")
                .withConnectionPoolSize(workers);

        DUUIComposer composer = new DUUIComposer().withLuaContext(context)
                .withWorkers(workers)
                .withStorageBackend(sqlite);
        DUUIDockerDriver dockerDriver = new DUUIDockerDriver()
                .withTimeout(timeout);
        DUUIRemoteDriver remoteDriver = new DUUIRemoteDriver(timeout);
        DUUIUIMADriver uimaDriver = new DUUIUIMADriver().withDebug(true);
        DUUISwarmDriver swarmDriver = new DUUISwarmDriver();

        composer.addDriver(dockerDriver, remoteDriver, uimaDriver, swarmDriver);

        composer.add(new DUUIDockerDriver
                .Component("docker.texttechnologylab.org/gnfinder:latest")
                .withScale(workers)
                .withImageFetching()
                .withName("DuuiComposer")
        );

        composer.add(new DUUIUIMADriver.Component(
                createEngineDescription()
        ).withScale(workers));

        composer.run(cas, "VideoDiarization");
    }

    private AnalysisEngineDescription createEngineDescription() {
        try {
            return AnalysisEngineFactory.createEngineDescription(
                    TTLabXmiWriter.class,
                    TTLabXmiWriter.PARAM_TARGET_LOCATION,
                    outputPath
            );
        } catch (ResourceInitializationException e) {
            throw new RuntimeException(e);
        }
    }

    public void start() {
        loadCas();
        System.out.println(cas);
        try {
            process2();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

}
