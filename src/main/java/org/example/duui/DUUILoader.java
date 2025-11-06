package org.example.duui;

import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;
import org.apache.commons.compress.compressors.CompressorException;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.cas.CASException;
import org.apache.uima.fit.factory.AnalysisEngineFactory;
import org.apache.uima.fit.factory.JCasFactory;
import org.apache.uima.fit.util.JCasUtil;
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
import org.texttechnologylab.annotation.type.AudioToken;
import org.xml.sax.SAXException;


import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;

public class DUUILoader {

    private JCas cas;

    public DUUILoader() {
    }

    private void loadCas() {
        try {
            cas = JCasFactory.createJCas();
            String videoName = "test-video";
            Path videoPath = Path.of("src/main/resources/"+ videoName +".mp4");
            byte[] bytes = Files.readAllBytes(videoPath);

            DocumentMetaData metaData = DocumentMetaData.create(cas);
            metaData.setDocumentTitle(videoName);
            metaData.setDocumentUri(videoPath.toString());
            metaData.setCollectionId(videoName);

            String base64 = Base64.getEncoder().encodeToString(bytes);
            cas.setSofaDataString(base64, "video/mp4");

        } catch (ResourceInitializationException e) {
            throw new RuntimeException(e);
        } catch (CASException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void process() throws Exception {
        DUUIComposer composer = new DUUIComposer()
                .withWorkers(1)
                .withSkipVerification(true)
                .withLuaContext(new DUUILuaContext().withJsonLibrary());
        composer.addDriver(new DUUIDockerDriver());
        composer.addDriver(new DUUIUIMADriver());
        composer.addDriver(new DUUIRemoteDriver());
        composer.add(
            new DUUIRemoteDriver.Component("localhost:8000")
                    .withScale(1)
                    .withTargetView("transcript")
                    .withParameter("language", "en")
                    .build()
                    .withTimeout(1000000000L)
        );
        composer.run(cas, "duui-diarization");

        System.out.println(cas.getView("transcript").getDocumentText());
        for (AudioToken token : JCasUtil.select(cas.getView("transcript"), AudioToken.class)) {
            System.out.println(token.getTimeStart() + " - " + token.getTimeEnd() + " | " + token.getBegin() + " - " + token.getEnd() + ": " + token.getCoveredText());
        }
    }

    public void start() {
        loadCas();
        System.out.println(cas);
        try {
            process();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

}
