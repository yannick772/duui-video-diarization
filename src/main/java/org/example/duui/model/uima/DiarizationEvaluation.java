package org.example.duui.model.uima;

import org.apache.uima.cas.impl.CASImpl;
import org.apache.uima.cas.impl.TypeImpl;
import org.apache.uima.cas.impl.TypeSystemImpl;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.JCasRegistry;
import org.apache.uima.jcas.cas.AnnotationBase;

import java.lang.invoke.CallSite;
import java.lang.invoke.MethodHandle;

public class DiarizationEvaluation extends AnnotationBase {
    public static final String _TypeName = "org.yhcompute.diarization.uima.type.DiarizationEvaluation";
    public static final int typeIndexID = JCasRegistry.register(DiarizationEvaluation.class);
    public static final int type;

    public static final String _FeatName_speakers = "speakers";
    private static final CallSite _FC_speakers;
    private static final MethodHandle _FH_speakers;

    public static final String _FeatName_avgLength = "avgLength";
    private static final CallSite _FC_avgLength;
    private static final MethodHandle _FH_avgLength;

    public static final String _FeatName_maxLength = "maxLength";
    private static final CallSite _FC_maxLength;
    private static final MethodHandle _FH_maxLength;

    public static final String _FeatName_minLength = "minLength";
    private static final CallSite _FC_minLength;
    private static final MethodHandle _FH_minLength;

    public static final String _FeatName_speakerSwaps = "speakerSwaps";
    private static final CallSite _FC_speakerSwaps;
    private static final MethodHandle _FH_speakerSwaps;

    public int getTypeIndexID() {
        return typeIndexID;
    }

    public DiarizationEvaluation(TypeImpl type, CASImpl casImpl) {
        super(type, casImpl);
        this.readObject();
    }

    public DiarizationEvaluation(JCas jcas) {
        super(jcas);
        this.readObject();
    }

    public DiarizationEvaluation(JCas jcas, int speakers, float avgLength, int maxLength, int minLength, int speakerSwaps) {
        super(jcas);
        this.setSpeakers(speakers);
        this.setAvgLength(avgLength);
        this.setMaxLength(maxLength);
        this.setMinLength(minLength);
        this.setSpeakerSwaps(speakerSwaps);
        this.readObject();
    }

    private void readObject() {
    }

    public int getSpeakers() {
        return this._getIntValueNc(wrapGetIntCatchException(_FH_speakers));
    }

    public void setSpeakers(int i) {
        this._setIntValueNfc(wrapGetIntCatchException(_FH_speakers), i);
    }

    public float getAvgLength() {
        return this._getFloatValueNc(wrapGetIntCatchException(_FH_avgLength));
    }

    public void setAvgLength(float f) {
        this._setFloatValueNfc(wrapGetIntCatchException(_FH_avgLength), f);
    }

    public int getMaxLength() {
        return this._getIntValueNc(wrapGetIntCatchException(_FH_maxLength));
    }

    public void setMaxLength(int i) {
        this._setIntValueNfc(wrapGetIntCatchException(_FH_maxLength), i);
    }

    public int getMinLength() {
        return this._getIntValueNc(wrapGetIntCatchException(_FH_minLength));
    }

    public void setMinLength(int i) {
        this._setIntValueNfc(wrapGetIntCatchException(_FH_minLength), i);
    }

    public int getSpeakerSwaps() {
        return this._getIntValueNc(wrapGetIntCatchException(_FH_speakerSwaps));
    }

    public void setSpeakerSwaps(int i) {
        this._setIntValueNfc(wrapGetIntCatchException(_FH_speakerSwaps), i);
    }

    static {
        type = typeIndexID;
        _FC_speakers = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_speakers);
        _FH_speakers = _FC_speakers.dynamicInvoker();
        _FC_avgLength = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_avgLength);
        _FH_avgLength = _FC_avgLength.dynamicInvoker();
        _FC_maxLength = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_maxLength);
        _FH_maxLength = _FC_maxLength.dynamicInvoker();
        _FC_minLength = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_minLength);
        _FH_minLength = _FC_minLength.dynamicInvoker();
        _FC_speakerSwaps = TypeSystemImpl.createCallSite(DiarizationToken.class, _FeatName_speakerSwaps);
        _FH_speakerSwaps = _FC_speakerSwaps.dynamicInvoker();
    }
}
