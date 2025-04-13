import { z } from "zod";

export const PdbFileSchema = z.object({
    id: z.string(),
    fileName: z.string(),
    fileContent: z.string(),
    createdAt: z.date().default(() => new Date()),
});
