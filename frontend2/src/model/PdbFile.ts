import mongoose, { Schema, Document } from "mongoose";

export interface PdbFile extends Document {
  id: string;
  fileName: string;
  fileContent: string;
  createdAt: Date;
}

const PdbFileSchema: Schema<PdbFile> = new Schema({
  id: { type: String, required: true },
  fileName: { type: String, required: true },
  fileContent: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
});

const PdbFileModel =
  (mongoose.models.PdbFile as mongoose.Model<PdbFile>) ||
  mongoose.model<PdbFile>("PdbFile", PdbFileSchema);

export default PdbFileModel;
