package org.example.duui.model.uima;

import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.JCasRegistry;
import org.apache.uima.jcas.tcas.Annotation;

public class VideoBase64 extends Annotation {

    public static final String _TypeName = "org.yhcompute.diarization.uima.type.VideoBase64";
    public static final int typeIndexID = JCasRegistry.register(VideoBase64.class);

    private DocumentMetaData metaData;

    private String base64Video;

    public VideoBase64(JCas cas) {
        super(cas);

    }

    public void setBase64Video(String base64Video) {
        this.base64Video = base64Video;
    }

    public String getBase64Video() {
        return base64Video;
    }

    public DocumentMetaData getMetaData() {
        return metaData;
    }

    public void setMetaData(DocumentMetaData metaData) {
        this.metaData = metaData;
    }
}
