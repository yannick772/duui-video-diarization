package org.example.duui.model;

import org.apache.uima.cas.CAS;
import org.apache.uima.cas.impl.CASImpl;
import org.apache.uima.cas.impl.TypeImpl;
import org.apache.uima.cas.impl.TypeSystemImpl;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.JCasRegistry;
import org.apache.uima.jcas.cas.AnnotationBase;
import org.apache.uima.jcas.cas.FSArray;
import org.apache.uima.jcas.tcas.Annotation;
import org.example.duui.model.uima.DiarizationEvaluation;
import org.example.duui.model.uima.DiarizationToken;
import org.texttechnologylab.annotation.AnnotatorMetaData;

import java.lang.invoke.CallSite;
import java.lang.invoke.MethodHandle;
import java.util.List;

public class DiarizationResult extends AnnotationBase {
    public final static String _TypeName = "org.yhcompute.diarization.uima.type.DiarizationResult";
    public final static int typeIndexID = JCasRegistry.register(DiarizationResult.class);

    public final static int type = typeIndexID;

    public final static String _FeatName_evaluation = "evaluation";
    public final static String _FeatName_tokens = "tokens";
    public final static String _FeatName_meta = "meta";

    @Override
    public int getTypeIndexID() {
        return typeIndexID;
    }

    private final static CallSite _FC_evaluation = TypeSystemImpl.createCallSite(DiarizationResult.class, _FeatName_evaluation);
    private final static MethodHandle _FH_evaluation = _FC_evaluation.dynamicInvoker();
    private final static CallSite _FC_tokens = TypeSystemImpl.createCallSite(DiarizationResult.class, _FeatName_tokens);
    private final static MethodHandle _FH_tokens = _FC_tokens.dynamicInvoker();
    private final static CallSite _FC_meta = TypeSystemImpl.createCallSite(DiarizationResult.class, _FeatName_meta);
    private final static MethodHandle _FH_meta = _FC_meta.dynamicInvoker();

    public DiarizationResult(JCas jcas) {
        super(jcas);
    }

    public DiarizationResult(TypeImpl t, CASImpl c) {
        super(t, c);
    }

    public final DiarizationEvaluation getEvaluation() {
        try {
            return (DiarizationEvaluation) _FH_evaluation.invokeExact();
        } catch (Throwable e) {
            throw new RuntimeException(e); // never happen
        }
    }
    public final FSArray<DiarizationToken> getTokens() {
        try {
            return (FSArray<DiarizationToken>) _FH_tokens.invokeExact();
        } catch (Throwable e) {
            throw new RuntimeException(e); // never happen
        }
    }

    public final AnnotatorMetaData getMeta() {
        try {
            return (AnnotatorMetaData) _FH_meta.invokeExact();
        } catch (Throwable e) {
            throw new RuntimeException(e); // never happen
        }
    }
}
