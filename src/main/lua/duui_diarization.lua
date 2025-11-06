StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")
Class = luajava.bindClass("java.lang.Class")
JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
-- switch to new utils, needs DUUI version >= 9d7a3e7c581ae7977763262397a4f533c6d7edec and rebuilt Dockers
SentimentUtils = luajava.bindClass("org.texttechnologylab.DockerUnifiedUIMAInterface.lua.DUUILuaUtils")

function serialize(inputCas, outputStream, parameters)  

    local video = inputCas::getSofaDataString()

    outputStream:write(json.encode({
        base64Video = video
    }))
end

function deserialize(inputCas, inputStream)
    local inputString = luajava.newInstance("java.lang.String", inputStream:readAllBytes(), StandardCharsets.UTF_8)
    local results = json.decode(inputString)

    if results["modification_meta"] ~= nil and results["meta"] ~= nil and results["diarization"] ~= nil then
        local modification_meta = results["modification_meta"]
        local modification_anno = luajava.newInstance("org.texttechnologylab.annotation.DocumentModification", inputCas)
        modification_anno:setUser(modification_meta["user"])
        modification_anno:setTimestamp(modification_meta["timestamp"])
        modification_anno:setComment(modification_meta["comment"])
        modification_anno:addToIndexes()

        local diarization = results["diarization"]
        local entireText = ""

        for i, token in ipairs(diarization["tokens"]) do
            if entireText == "" then
                entireText = entireText .. token["text"]
            else
                entireText = entireText .. " " .. token["text"]
            end

            local token_anno = luajava.newInstance("org.yhcompute.diarization.uima.type.DiarizationToken", inputCas)
            token_anno::setBegin(token["begin"])
            token_anno::setEnd(token["end"])
            token_anno::setSpeaker(token["speaker"])
            token_anno::setText(token["text"])
            token_anno::setTimeStart(token["timeStart"])
            token_anno::setTimeEnd(token["timeEnd"])
            token_anno::addToIndexes()

            local meta = token["meta"]

            local meta_anno = luajava.newInstance("org.texttechnologylab.annotation.AnnotatorMetaData", inputCas)
            meta_anno:setReference(token_anno)
            meta_anno:setName(meta["name"])
            meta_anno:setVersion(meta["version"])
            meta_anno:setModelName(meta["modelName"])
            meta_anno:setModelVersion(meta["modelVersion"])
            meta_anno:addToIndexes()

        inputCas:setSofaDataString(entireText, "text/plain")
    end
end