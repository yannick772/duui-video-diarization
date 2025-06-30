package org.example.duui.model.uima;

import org.apache.uima.jcas.tcas.Annotation;

import java.util.List;

public class UimaVideo extends Annotation {
    private String name;

    private List<UimaFrame> videoFrames;

    private UimaAudio audio;

    private int fps;

    public int getFps() {
        return fps;
    }

    public void setFps(int fps) {
        this.fps = fps;
    }

    public List<UimaFrame> getVideoFrames() {
        return videoFrames;
    }

    public void setVideoFrames(List<UimaFrame> videoFrames) {
        this.videoFrames = videoFrames;
    }

    public UimaAudio getAudio() {
        return audio;
    }

    public void setAudio(UimaAudio audio) {
        this.audio = audio;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
