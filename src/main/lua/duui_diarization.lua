StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")
-- Class = luajava.bindClass("java.lang.Class")
-- JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")

function serialize(inputCas, outputStream, parameters)  

    local video = inputCas:getSofaDataString()

    outputStream:write(json.encode({
        base64Video = video
    }))
end

function deserialize(inputCas, inputStream)
    local inputString = luajava.newInstance("java.lang.String", inputStream:readAllBytes(), StandardCharsets.UTF_8)
    local response = json.decode(inputString)

    if response["modification_meta"] ~= nil and response["meta"] ~= nil and response["diarization"] ~= nil then
        local modification_meta = response["modification_meta"]
        local modification_anno = luajava.newInstance("org.texttechnologylab.annotation.DocumentModification", inputCas)
        modification_anno:setUser(modification_meta["user"])
        modification_anno:setTimestamp(modification_meta["timestamp"])
        modification_anno:setComment(modification_meta["comment"])
        modification_anno:addToIndexes()

        for i, diarization in ipairs["diarization"] do
            local meta = token["meta"]

            local meta_anno = luajava.newInstance("org.texttechnologylab.annotation.AnnotatorMetaData", inputCas)
            meta_anno:setReference(token_anno)
            meta_anno:setName(meta["name"])
            meta_anno:setVersion(meta["version"])
            meta_anno:setModelName(meta["modelName"])
            meta_anno:setModelVersion(meta["modelVersion"])
            -- meta_anno:addToIndexes()

            local token_list = luajava.newInstance("uima.cas.FSArray")
            local entireText = ""

            for j, token in ipairs(diarization["tokens"]) do
                if entireText == "" then
                    entireText = entireText .. token["text"]
                else
                    entireText = entireText .. " " .. token["text"]
                end

                local token_anno = luajava.newInstance("org.yhcompute.diarization.uima.type.DiarizationToken", inputCas)
                token_anno:setBegin(token["begin"])
                token_anno:setEnd(token["end"])
                token_anno:setSpeaker(token["speaker"])
                token_anno:setText(token["text"])
                token_anno:setTimeStart(token["timeStart"])
                token_anno:setTimeEnd(token["timeEnd"])
                -- token_anno:addToIndexes()
                token_list:set(j, token_anno)
            end

            diarization_anno = luajava.newInstance("org.yhcompute.diarization.uima.type.DiarizationResult", inputCas)
            diarization_anno:setTokens(token_list)
            diarization_anno:setMeta(meta_anno)
            diarization_anno:addToIndexes()

        end

        inputCas:setSofaDataString(entireText, "text/plain")
    end
end