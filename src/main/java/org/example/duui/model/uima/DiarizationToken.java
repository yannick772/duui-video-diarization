package org.example.duui.model.uima;

import org.apache.uima.cas.impl.CASImpl;
import org.apache.uima.cas.impl.TypeImpl;
import org.apache.uima.cas.impl.TypeSystemImpl;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.JCasRegistry;
import org.texttechnologylab.annotation.type.MultimediaElement;

import java.lang.invoke.CallSite;
import java.lang.invoke.MethodHandle;

public class DiarizationToken extends MultimediaElement {
    public static final String _TypeName = "org.yhcompute.diarization.uima.type.DiarizationToken";
    public static final int typeIndexID = JCasRegistry.register(DiarizationToken.class);
    public static final int type;

    public static final String _FeatName_speaker = "speaker";
    private static final CallSite _FC_speaker;
    private static final MethodHandle _FH_speaker;

    public static final String _FeatName_text = "text";
    private static final CallSite _FC_text;
    private static final MethodHandle _FH_text;

    public int getTypeIndexID() {
        return typeIndexID;
    }

    public DiarizationToken(TypeImpl type, CASImpl casImpl) {
        super(type, casImpl);
        this.readObject();
    }

    public DiarizationToken(JCas jcas) {
        super(jcas);
        this.readObject();
    }

    public DiarizationToken(JCas jcas, int begin, int end) {
        super(jcas);
        this.setBegin(begin);
        this.setEnd(end);
        this.readObject();
    }

    private void readObject() {
    }

    public int getSpeaker() {
        return this._getIntValueNc(wrapGetIntCatchException(_FH_speaker));
    }

    public void setSpeaker(int s) {
        this._setFloatValueNfc(wrapGetIntCatchException(_FH_speaker), s);
    }

    public String getText() {
        return this._getStringValueNc(wrapGetIntCatchException(_FH_text));
    }

    public void setText(String t) {
        this._setStringValueNfc(wrapGetIntCatchException(_FH_text), t);
    }

    static {
        type = typeIndexID;
        _FC_speaker = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_speaker);
        _FH_speaker = _FC_speaker.dynamicInvoker();
        _FC_text = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_text);
        _FH_text = _FC_text.dynamicInvoker();
    }


}
